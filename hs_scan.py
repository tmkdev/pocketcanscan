import os
import pygame
import time
import datetime
import random
import logging
import sys
import textwrap
from collections import deque
import itertools

import can4python as can
import RPi.GPIO as GPIO

import config
import utils

config = config.loadconfig('config.yml')

GPIO.setmode(GPIO.BCM)
joy_left = 5
joy_right = 26
joy_up = 6
joy_down = 19
GPIO.setup(joy_up, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(joy_down, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(joy_left, GPIO.IN, GPIO.PUD_UP)
#GPIO.setup(joy_right, GPIO.IN, GPIO.PUD_UP)

bus = can.CanBus.from_kcd_file(config['kcd'], config['canbus'])

os.environ["SDL_FBDEV"] = "/dev/fb1"

class HS_Scan:
    screen = None;
    fontcolor = (0, 255, 0)
    white = (255, 255, 255)
    black = (0,0,0)
    red = (255,0,0)

    candata = {}
    canhistory = {}

    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            logging.warning( "I'm running under X display = {0}".format(disp_no))

        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                logging.warning('Driver: {0} failed.'.format(driver))
                continue
            found = True
            break

        if not found:
            raise Exception('No suitable video driver found!')

        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        logging.warning("Framebuffer size: %d x %d" % (size[0], size[1]))
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))
        # Initialise font support
        pygame.font.init()
        # Render the screen
        pygame.mouse.set_visible(False)

        self.font = pygame.font.Font('../segoeui.ttf', 12)
        self.font2 = pygame.font.Font('../segoeui.ttf', 10)

        pygame.display.update()

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

    def scan(self):
        self.canhistory = utils.createhistory(config['displays']['all'])
        wrapper = textwrap.TextWrapper(width=22)

        curpos = 0
        menu_iter = itertools.cycle(config['displays'].keys())

        curmenu = next(menu_iter)

        while True:

            if not GPIO.input(joy_up):
                curpos-=1
                if curpos < 0:
                    curpos=0
                time.sleep(0.2)

            if not GPIO.input(joy_down):
                curpos+=1
                time.sleep(0.2)

            if not GPIO.input(joy_left):
                curmenu = next(menu_iter)
                time.sleep(0.2)

            received_signalvalues = bus.recv_next_signals()
            if received_signalvalues:
                self.candata = { **self.candata, **received_signalvalues }
                for signal in received_signalvalues:
                    if signal in self.canhistory:
                        self.canhistory.append(received_signalvalues['signal'])

                self.updateKPIs(config['displays'][curmenu], curpos)

    def updateKPIs(self, kpilist, curpos):
        wrapper = textwrap.TextWrapper(width=22)
        currentline = 0
        self.screen.fill(self.black)

        for sig in sorted(kpilist)[curpos:]:
            sig_sub = sig.replace('_', ' ')
            sig_wrap = wrapper.wrap(sig_sub)
            for line in sig_wrap:
                text = self.font2.render(line.upper(), False, self.fontcolor)
                self.screen.blit(text, (0,currentline*12))
                currentline+=1
            try:
                text = self.font.render(str(self.candata[sig]), False, self.white)
            except:
                text = self.font.render('N/A', False, self.red)

            self.screen.blit(text, (0,currentline*12))
            currentline +=1

            if currentline > 9:
                break

        pygame.display.update()

    def updateGraph(self, kpi):
        raise NotImplemented

if __name__ == '__main__':
    scanner = HS_Scan()
    scanner.scan()


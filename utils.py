from collections import deque

def createhistory(all_signals, history_size=128):
    history = {}

    for signal in all_signals:
        history[signal] = deque([], maxlen=history_size)

    return history
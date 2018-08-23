import can4python
import yaml

def canbus_signals(kcd):
    config = can4python.FilehandlerKcd.read('gm_global_a_hs.kcd')
    signames = get_signal_names(config)
    s = {'displaysignals': signames }

    print(yaml.dump(s, default_flow_style=False))

def get_signal_names(config):
    signal_names = []

    for arb_id in config.framedefinitions:
        sig_defs = config.framedefinitions[arb_id].signaldefinitions
        for sig in sig_defs:
            signal_names.append(sig.signalname)

    return sorted(signal_names)


if __name__ == '__main__':
    canbus_signals('gm_global_a_hs.kcd' )
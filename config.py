import yaml

def loadconfig(config_file):
    with open(config_file, 'r') as conf:
        config = yaml.load(conf)
    return config


if __name__ == '__main__':
    config = loadconfig('config.yml')
    print(config)
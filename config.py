import yaml

with open('config.yml') as conf:
    print(yaml.load(conf))
    
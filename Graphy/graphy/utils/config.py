import json

from graphy.utils import files


def get(module):
    with open(files.get_absolute_path('graphy/config.json', True)) as f:
        config = json.load(f)
    return config[module]

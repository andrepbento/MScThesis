"""
    Author: André Bento
    Date last modified: 21-02-2019
"""
import logging
import logging.config

import coloredlogs
import yaml

from graphy.utils import files


def setup_logging(name, default_path='graphy/logging.yaml', default_level=logging.INFO):
    """ Setup logging configuration """
    path = files.get_absolute_path(default_path, from_project=True)
    try:
        with open(path, 'r') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
            coloredlogs.install()
            logger = logging.getLogger(__name__)
            logger.info('logger')
            logging.info('logging')
    except Exception as e:
        print(e)  # 'Failed to load configuration file. Using default configs'
        logging.basicConfig(level=default_level)
        coloredlogs.install(level=default_level)
    return logging.getLogger(name)

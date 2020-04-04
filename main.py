from logging.config import dictConfig
from os.path import abspath, join, dirname

import yaml

from music_playlists.process import Process

with open(abspath(join(dirname(abspath(__file__)), 'data', 'logging.yml')), 'rt') as f:
    # config logging
    config = yaml.safe_load(f)
    dictConfig(config)

if __name__ == '__main__':
    processing = Process()
    processing.run()

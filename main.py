from logging.config import dictConfig

from music_playlists.process import Process

dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)-8s] %(name)s: %(message)s',
            'level': 'INFO',
            'datefmt': '%Y-%m-%dT%H:%M:%S%z',
        }
    },
    'handlers': {
        'standard': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        }
    },
    'loggers': {
        'music_playlists': {
            'level': 'INFO',
            'handlers': ['standard'],
            'propagate': False,
        },
        'gmusicapi': {
            'level': 'INFO',
            'handlers': ['standard'],
            'propagate': False,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['standard']
    }
})

if __name__ == '__main__':
    processing = Process()
    processing.run()

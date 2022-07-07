import logging
import logging.config

'''
#_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"

def get_file_handler():
    file_handler = logging.FileHandler("x.log")
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler

def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())
    return logger
'''


def configure_logger():
    DEFAULT_LOGGING = {

            'version': 1,
            'disable_existing_loggers': True,
            "root":{
                "handlers" : ["console1"],
                "level": "DEBUG"
            },
            'loggers': {
                '': {
                    'level': 'INFO',
                },
                'dgus.display.communication.communication_interface': {
                    'handlers' : [ 'console1' ],
                    'propagate' : False,
                    'level' : 'INFO'
                },
                'dgus.display.display': {
                    'handlers' : [ 'console1' ],
                    'propagate' : False,
                    'level' : 'DEBUG'
                },
                'jsonmerge' : {
                    'handlers' : [ 'console1' ],
                    'propagate' : False,
                    'level' : 'WARN'
                },
                'websocket' : {
                    'handlers' : [ 'console1' ],
                    'propagate' : False,
                    'level' : 'DEBUG'
                }
            },
            'handlers' : {
            'console1' : {
                'formatter' : 'std_out1',
                'class' : 'logging.StreamHandler',
                'level' : 'DEBUG'
            }
            },
            'formatters' : {
                'std_out1' : {
                    'format' : '%(asctime)s : %(levelname)-5s : %(name)s : %(funcName)s : %(message)s',
                    'datefmt' : '%Y-%m-%d %I:%M:%S'
                }
            }
    }

    logging.config.dictConfig(DEFAULT_LOGGING)
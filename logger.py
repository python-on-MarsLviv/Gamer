from logging.handlers import TimedRotatingFileHandler
import logging

class FileHandler(logging.Handler):
    def __init__(self, filename):
        logging.Handler.__init__(self)
        self.filename = filename

    def emit(self, record):
        message = self.format(record)
        with open(self.filename, 'w') as file:
            file.write(message + '\n')

logger_config = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'std_format': {
            'format': '{asctime} [{levelname}|{name}] [{module}:{funcName}:{lineno}] {message}',
            'style': '{'
        },
        'log_format': {
            'format': '{asctime} [{levelname}|{name}] [{module}:{funcName}:{lineno}] {message}',
            'style': '{'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'std_format'
        },
        'file_rotate': {
            '()': TimedRotatingFileHandler,
            'when': 'd',
            'interval': 1,
            'level': 'INFO',
            'filename': 'gamer.log',
            'formatter': 'log_format'
        },
        'file_write': {
            '()': FileHandler,
            'level': 'DEBUG',
            'filename': 'change_this_name_and_interval_in_logger.py.log',
            'formatter': 'std_format'
        }
    },
    'loggers': {
        'app_logger': {
            'level': 'DEBUG',
            'handlers': ['file_rotate']
            #'propagate': False
        },
        'app_debugger': {
            'level': 'DEBUG',
            'handlers': ['console']
            #'propagate': False
        }
    },
}

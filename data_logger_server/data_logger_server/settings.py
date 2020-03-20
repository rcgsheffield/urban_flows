"""
Web app configuration
"""

import os.path

from settings_local import *

# Web server response configuration
RESPONSE_TEMPLATE_PATH = 'response_template.xml'
RESPONSE_MIME_TYPE = 'application/xml'

# Directory in which to place data files received from the web
TEMP_SUFFIX = '.tmp'  # suffix for temporary files (i.e. during write operation)
TEMP_DIR = None  # temporary files location (defaults to the same as DATA_DIR)

# Logging configuration
LOG_DIR = 'logs'
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'standard': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(levelname)s %(module)s: %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'ERROR',
            'when': 'D',
            'filename': os.path.join(LOG_DIR, 'error.log'),
            'formatter': 'standard',
        },
        'file_info': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'INFO',
            'when': 'D',
            'filename': os.path.join(LOG_DIR, 'info.log'),
            'formatter': 'standard',
        },
        'email': {
            'class': 'logging.handlers.SMTPHandler',
            'level': 'ERROR',
            'mailhost': 'smtp.shef.ac.uk',
            'fromaddr': 'noreply@shef.ac.uk',
            'toaddrs': [
                'j.heffer@sheffield.ac.uk',
            ],
            'subject': 'Data logger server error',
        }
    },
    # root logger
    'root': {
        'level': 'INFO',
        'handlers': ['file', 'file_info', 'console', 'email'],
    },
}

"""
Web app configuration
"""

from settings_local import *

# Web server response configuration
RESPONSE_TEMPLATE_PATH = 'response_template.xml'

# Directory in which to place data files received from the web
# suffix for temporary files (i.e. during write operation)
TEMP_SUFFIX = '.tmp'
# temporary files location (defaults to the same as DATA_DIR)
TEMP_DIR = None

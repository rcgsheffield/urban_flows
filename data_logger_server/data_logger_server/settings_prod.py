"""
Machine-specific configuration files
"""

import pathlib

ROOT_DIR = pathlib.Path('/home/uflo/dlsrv')

# Subdirectories
DATA_DIR = ROOT_DIR.joinpath('senddata')
ALARM_DIR = ROOT_DIR.joinpath('sendalarm')

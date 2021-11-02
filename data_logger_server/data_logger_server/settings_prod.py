"""
Machine-specific configuration files
"""

import pathlib

ROOT_DIR = pathlib.Path('/home/uflo/dlsrv')

DATA_DIR = ROOT_DIR.joinpath('senddata')
ALARM_DIR = ROOT_DIR.joinpath('sendalarm')

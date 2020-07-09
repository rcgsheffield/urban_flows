import pathlib

DATE_FORMAT = '%Y-%m-%d'
DEFAULT_CONFIG_FILE = str(pathlib.Path.home().joinpath('airsonde.cfg'))
FAMILY = 'EMS_AirSonde'
DESC_URL = 'https://terminal.oizom.com/#/u/devices/info'

METRICS = dict(
    # uv = ultraviolet index
    # light = lux
    temp='MET_TEMP',
    hum='MET_RH',
    bs='INST_BATTERY_PERCENT',  # battery strength
)

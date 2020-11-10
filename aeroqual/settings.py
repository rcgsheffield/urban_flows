import csv
import pathlib

CONFIG_DIR = pathlib.Path.home().joinpath('configs')
DEFAULT_CONFIG_FILE = CONFIG_DIR.joinpath('aeroqual.cfg')

LOGGING = dict(
    # https://docs.python.org/3.8/library/logging.html#logrecord-attributes
    format='%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s',
)

DEFAULT_AVERAGING_PERIOD = 1

# Rename metrics from the values on the remote API to the UFO standard
RENAME_COLUMNS = {
    'Time': 'timestamp',
    'NO2': 'AQ_NO2',
    'O3': 'AQ_O3',
    'PM2.5': 'AQ_PM25',
    'PM10': 'AQ_PM10',
    'TEMP': 'MET_TEMP',
    'RH': 'MET_RH',
    'DP': 'DEW_POINT',
    'Ox': 'AQ_OX',  # OX = O3 + NO2
    'O3 raw': 'AQ_O3_RAW',
    'PM10 raw': 'AQ_PM10_RAW',
    'PM2.5 raw': 'AQ_PM25_RAW',

}

SELECTED_COLUMNS = [
    'timestamp',
    'AQ_NO2',
    'AQ_O3',
    'AQ_PM25',
    'MET_TEMP',
    'MET_RH',
    'DEW_POINT',
]

# Metadata assets
DESC_URL = 'https://cloud.aeroqual.com'
FAMILY = 'Aeroqual'


class UrbanDialect(csv.excel):
    """
    CSV format for Urban Flows
    """
    delimiter = '|'


API_BASE_URL = 'https://cloud.aeroqual.com/api/'

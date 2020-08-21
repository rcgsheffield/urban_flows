import pathlib

DATE_FORMAT = '%Y-%m-%d'
USER_AGENT = 'Urban Flows Observatory'
BOUNDING_BOX = 'sheffield_bounding_box_geojson.json'

# List generated using metadata utility script
CONFIG_DIR = pathlib.Path.home().joinpath('configs')
DEFAULT_SAMPLING_FEATURES_PATH = CONFIG_DIR.joinpath('defra_sos_sampling_features.txt')

# Build default serialisation directories
DEFAULT_RAW_DIR = str(pathlib.Path('data').joinpath('raw'))

OUTPUT_HEADERS = (
    'timestamp',
    'sensor',
    'AQ_CO',
    'AQ_NO2',
    'AQ_NOX',
    'AQ_O3',
    'AQ_PM10',
    'AQ_PM25',
    'AQ_SO2',
    'AQ_NO',
)

# Metadata
COUNTRY = 'United Kingdom'
FAMILY = 'DEFRA'

# Local authority region https://uk-air.defra.gov.uk/data/API/local-authority-region
REGION_OF_INTEREST = 17  # South Yorkshire

# CSV options
DEFAULT_SEPARATOR = '|'

# Logging
LOGGING = dict(
    # https://docs.python.org/3.8/library/logging.html#logrecord-attributes
    format='%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s',
)

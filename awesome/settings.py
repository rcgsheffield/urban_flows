import datetime
import pathlib

# Authentication token
CONFIG_PATH = pathlib.Path.home().joinpath('configs')
DEFAULT_TOKEN_PATH = CONFIG_PATH.joinpath('awesome_token.txt')
SENSOR_BOOKMARK_PATH = CONFIG_PATH.joinpath('sensor_bookmarks.json')
SITE_BOOKMARK_PATH = CONFIG_PATH.joinpath('site_bookmarks.json')

# The beginning of data collection
TIME_START = datetime.datetime(2020, 9, 20, tzinfo=datetime.timezone.utc)

# Log config
LOGGING = dict(
    format="%(levelname)s %(asctime)s %(filename)s:%(lineno)d %(message)s",
)

# The maximum number of readings to upload at once to /api/reading/bulk. The limit is 100.
BULK_READINGS_CHUNK_SIZE = 100

DEFAULT_READING_TYPE_GROUPS_FILE = 'reading_type_groups.json'
DEFAULT_AQI_STANDARDS_FILE = 'aqi-standards.json'

BASE_URL = 'http://ufportal.shef.ac.uk/api/'

AQI_TIME_AVERAGE_FREQUENCY = '1min'

URBAN_FlOWS_TIME_CHUNK = datetime.timedelta(days=31)

UF_COLUMN_RENAME = {
    'ID_MAIN': 'sensor',
    'TIME_UTC_UNIX': 'time',
}

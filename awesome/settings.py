import datetime
import pathlib

from settings_local import *

# Authentication token
CONFIG_PATH = pathlib.Path.home().joinpath('configs')
DEFAULT_TOKEN_PATH = CONFIG_PATH.joinpath('awesome_token.txt')
SITE_BOOKMARK_PATH = CONFIG_PATH.joinpath('site_bookmarks.json')

# The beginning of data collection
TIME_START = datetime.datetime(2019, 1, 1, tzinfo=datetime.timezone.utc)

# Log config
LOGGING = dict(
    format="%(levelname)s %(asctime)s %(filename)s:%(lineno)d %(message)s",
)

# The maximum number of readings to upload at once to /api/reading/bulk. The limit is 100.
BULK_READINGS_CHUNK_SIZE = 100

AQI_TIME_AVERAGE_FREQUENCY = '1min'

URBAN_FlOWS_TIME_CHUNK = datetime.timedelta(days=31)

# Assume there's only one AQI standard that has this identifier on the remote server
AWESOME_AQI_STANDARD_ID = 62

# Air quality standards configuration. By default, the first item in this list will be used and any others will be
# ignored.
AQI_STANDARDS = [
    {
        "name": "Daily Air Quality Index",
        "description": "https://uk-air.defra.gov.uk/air-pollution/daqi",
        "breakpoints": [
            {
                "min": 1,
                "max": 3,
                "color": "green"
            },
            {
                "min": 4,
                "max": 6,
                "color": "amber"
            },
            {
                "min": 7,
                "max": 9,
                "color": "red"
            },
            {
                "min": 10,
                "max": 10,
                "color": "violet"
            }
        ]
    }
]

# Configuration to group reading types into reading categories
READING_TYPE_GROUPS = [
    {
        "name": "Air Quality",
        "icon_name": "aq_marker.png",
        "reading_types": [
            "PM10",
            "PM2.5",
            "PM1"
        ]
    },
    {
        "name": "Atmosphere",
        "icon_name": "atmos_marker.png",
        "reading_types": [
            "AIRTEMP",
            "RELHUM",
            "ATMPRESS"
        ]
    }
]

# The quality score for each UFO sensor family
FAMILY_RATING = dict(
    AMfixed=1,
)

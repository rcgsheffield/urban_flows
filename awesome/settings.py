import datetime
import pathlib
import os

import settings_local

BASE_URL = os.getenv('AWESOME_BASE_URL', settings_local.BASE_URL)

# Authentication token
CONFIG_PATH = pathlib.Path.home().joinpath('configs')
DEFAULT_TOKEN_PATH = CONFIG_PATH.joinpath('awesome_token.txt')
# This will create files with bak,
BOOKMARK_PATH_PREFIX = CONFIG_PATH.joinpath('awesome_bookmarks')

# The beginning of data collection
TIME_START = datetime.datetime(2021, 3, 1, tzinfo=datetime.timezone.utc)

# Log config
LOGGING = dict(
    format="%(levelname)s %(asctime)s %(filename)s:%(lineno)d %(message)s",
)

# The maximum number of readings to upload at once to /api/reading/bulk
BULK_READINGS_CHUNK_SIZE = 100

AQI_TIME_AVERAGE_FREQUENCY = '1min'

# UFO data is partitioned on disk by family and day
URBAN_FlOWS_TIME_CHUNK = datetime.timedelta(days=1)

# Assume there's only one AQI standard that has this identifier on the remote
# server
AWESOME_AQI_STANDARD_ID = 62

# Air quality standards configuration. By default, the first item in this list
# will be used and any others will be ignored.
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

# Group reading types into reading categories
READING_TYPE_GROUPS = [
    {
        "name": "Air Quality",
        "icon_name": "aq_marker.png",
        "reading_types": [
            "AQ_PM10",
            "AQ_PM25",
            "AQ_PM1",
            "AQ_PM4",
            "AQ_PMSUM",
            "AQ_NOISE",
            "AQ_CO",
            "AQ_NO",
            "AQ_NO2",
            "AQ_PART_DENSITY",
            "AQ_O3",
            "AQ_SO2",
        ]
    }, {
        "name": "Atmosphere",
        "icon_name": "atmos_marker.png",
        "reading_types": [
            "MET_TEMP",
            "MET_RH",
            "MET_AP",
        ]
    },
    {
        "name": "Instrument",
        "icon_name": "inst_marker.png",
        "reading_types": [
            "INST_BATTERY_VOLTAGE",
        ]
    },
    {
        "name": "Traffic",
        "icon_name": "traff_marker.png",
        "reading_types": [
            "TRAFF_COUNTS",
            "TRAFF_FLOW",
            "TRAFF_INTERVAL",
        ]
    },
]

# The quality score for each UFO sensor family
FAMILY_RATING = dict(
    AMfixed=1,
)

# Urban Flows connection details
# Hostname used for SSH connection
HOST = 'ufdev.shef.ac.uk'
# URL built using same host
URL = 'http://{host}/uflobin/ufdexF1'.format(host=HOST)

# yyyy-MM-dd HH:mm:ss
AWESOME_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

AQI_TIME_BUFFER = dict(hours=24)

# Smooth AQI readings over time
AQI_ROUND_MINUTES = 15

from collections import OrderedDict

# Map environment agency API labels to Urban Obs.
# https://environment.data.gov.uk/flood-monitoring/doc/reference#measures
PARAMETER_MAP = OrderedDict(
    [
        ('level', 'WATER_LEVEL'),
        ('flow', 'WATER_FLOW'),
        ('wind', 'WIND_SPEED'),
        ('temperature', 'MET_TEMP'),
        ('rainfall', 'RAINFALL'),
    ]
)

DATE_FORMAT = '%Y-%m-%d'
DEFAULT_STATIONS_FILE = 'stations.txt'
DEFAULT_MEASURES_FILE = 'measures.txt'
DEFAULT_LATITUDE = 53.37
DEFAULT_LONGITUDE = -1.47
DEFAULT_DISTANCE = 30

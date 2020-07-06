import pathlib
from collections import OrderedDict

DEFAULT_CONFIG_PATH = pathlib.Path.home().joinpath('earthsense.cfg')

# Map EarthSense fields to Urban Flows Observatory structure
# The order of the items determines that of the columns in the output CSV file.
FIELD_MAP = OrderedDict(
    (
        ('Timestamp', 'timestamp'),
        ('device_id', 'sensor'),
        ('Temp', 'MET_TEMP'),
        ('Ambient temp', 'MET_TEMP_AMBIENT'),
        ('Ambient pressure', 'MET_AP'),
        ('Ambient humidity', 'MET_HUMIDITY_AMBIENT'),
        ('Humidity', 'MET_RH'),
        ('NO2', 'AQ_NO2'),
        ('NO', 'AQ_NO'),
        ('O3', 'AQ_O3'),
        ('PM2.5', 'AQ_PM25'),
        ('PM10', 'AQ_PM10'),
        ('PM1', 'AQ_PM1'),
    )
)

UNITS = {
    'NO2': 'ug/m3',
    'PM10': 'ug/m3',
    'PM2.5': 'ug/m3',
    'Temp': 'C',
    'Longitude': 'degrees',
    'Ambient temp': 'C',
    'NO': 'ug/m3',
    'PM1': 'ug/m3',
    'Humidity': '%RH',
    'Latitude': 'degrees',
    'O3': 'ug/m3',
    'Ambient pressure': 'Pa',
    'Ambient humidity': '%RH'
}

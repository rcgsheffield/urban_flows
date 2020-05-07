import os.path
from collections import OrderedDict

DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser('~'), 'earthsense.cfg')

# Map EarthSense fields to Urban Flows Observatory structure
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

NULL = -32768

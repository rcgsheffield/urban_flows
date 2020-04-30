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

NULL = -32767

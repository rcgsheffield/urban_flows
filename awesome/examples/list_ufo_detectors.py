import assets
from pprint import pprint

sites, families, pairs, sensors = assets.get_metadata()

detectors = assets.get_detectors_from_sensors(sensors)

pprint(detectors)

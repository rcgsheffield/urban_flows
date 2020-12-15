from pprint import pprint

import sync

sites, families, pairs, sensors, detectors = sync.get_urban_flows_metadata()

pprint(detectors)

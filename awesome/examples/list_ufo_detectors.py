import assets
import sys
import logging
import csv

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    sites, families, pairs, sensors = assets.get_metadata()

    detectors = assets.get_detectors_from_sensors(sensors)

    rows = (dict(current_name=detector_id, name=detector['name']) for detector_id, detector in detectors.items())

    # CSV output
    writer = csv.DictWriter(sys.stdout, fieldnames=['current_name', 'name'])
    writer.writeheader()
    writer.writerows(rows)

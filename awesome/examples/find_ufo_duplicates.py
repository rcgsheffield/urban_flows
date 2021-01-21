import logging
import itertools
import assets

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    sites, families, pairs, sensors = assets.get_metadata()
    detectors = list(itertools.chain(*(s['detectors'].values() for s in sensors)))

    site_names = {site['name'] for site in sites}

    sensor_names = {sensor['name'] for sensor in sensors}
    sensor_names_lower = {s.casefold() for s in sensor_names}

    detector_names = {detector['o'] for detector in detectors}

    for sensor in sensors:
        detector_names.update(sensor['varsByOnto'])

    if len(sensor_names_lower) != len(sensor_names):
        raise ValueError

    if len(detector_names) != len({s.casefold() for s in detector_names}):
        raise ValueError

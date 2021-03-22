import assets
import maps

if __name__ == '__main__':
    sites, families, pairs, sensors = assets.get_metadata()
    detectors = assets.Sensor.get_detectors_from_sensors(sensors)

    for detector_name, detector in detectors.items():
        print(detector_name)
        print(detector)
        print(maps.detector_to_reading_type(detector))
        print()

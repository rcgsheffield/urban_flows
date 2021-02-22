import assets

if __name__ == '__main__':
    sites, families, pairs, sensors = assets.get_metadata()

    for sensor_name, sensor in sensors.items():
        if '25612' in sensor_name.casefold():
            print(sensor_name, sensor)

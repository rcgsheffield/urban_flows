SELECT
     readings.created
    ,readings.value
    ,readings.location_id
    ,locations.name AS location
    ,reading_types.name AS reading_type
    ,readings.sensor_id
    ,sensors.name AS sensor
    ,sensor_types.name AS sensor_type
FROM portal.readings
LEFT JOIN portal.locations ON readings.location_id = locations.id
LEFT JOIN portal.reading_types ON readings.reading_type_id = reading_types.id
LEFT JOIN portal.sensors ON readings.sensor_id = sensors.id
LEFT JOIN portal.sensor_types ON sensors.sensor_type_id = sensor_types.id
WHERE readings.created >= CURRENT_DATE
    AND readings.sensor_id = 1357 -- 731
    AND reading_types.name = 'AQ_CO'
ORDER BY readings.created;

SELECT
     CAST(aqi_readings.created AS DATE) AS day_
    ,aqi_readings.created AS time_
    ,aqi_readings.value AS air_quality_index
    ,aqi_readings.location_id
    ,locations.name AS location
    ,locations.description
FROM portal.aqi_readings
LEFT JOIN portal.locations ON aqi_readings.location_id = locations.id
WHERE locations.id = 915 -- S0029
ORDER BY created DESC;

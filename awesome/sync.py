import datetime
import http
import time
import json
import logging
import pathlib
from typing import Type, List, Union, Mapping, MutableMapping
import requests

import assets
import exceptions
import http_session
import maps
import objects
import settings
import ufdex
import utils
import aqi.operations
import cache

LOGGER = logging.getLogger(__name__)

Path = Union[pathlib.Path, str]


def sync_readings(session, families: Mapping[str, dict],
                  awesome_sensors: Mapping, reading_types: Mapping,
                  start_time: datetime.datetime = None,
                  end_time: datetime.datetime = None):
    """
    Bulk store readings by iterating over sensors on the Urban Flows platform
    and uploading readings to the Awesome portal using the bulk upload API
    endpoint. Each sensor sync should proceed from the newest reading to avoid
    duplication.

    :param session: HTTP session for Awesome portal
    :param families: UFO families, key-value pairs of family names and metadata
    :param awesome_sensors: Awesome portal sensors
    :param reading_types: Awesome portal reading types
    :param start_time: Retrieve data created since this time
    :param end_time: Retrieve data up until this time
    """
    # Get all data up to the present time (when this function first runs)
    end_time = end_time or datetime.datetime.now(datetime.timezone.utc)

    # Count the number of readings uploaded for all the sensors
    total_reading_count = 0

    bookmarks = cache.Cache('readings')

    # Iterate over UFO sensor families
    for family_id, family in families.items():

        # Count the number of readings uploaded per family
        reading_count = 0

        # Begin where we left off, or go back to the beginning of time
        start_time = bookmarks.get(family_id, start_time or
                                   settings.TIME_START)

        LOGGER.info("Syncing readings for UFO family '%s' starting at %s",
                    family_id, start_time.isoformat())

        # Query UFO database by chunking over time periods
        for _start, _end in ufdex.UrbanFlowsQuery.generate_time_periods(
                start=start_time,
                end=end_time,
                freq=settings.URBAN_FlOWS_TIME_CHUNK
        ):
            query = ufdex.UrbanFlowsQuery(
                families={family_id},
                time_period=[_start, _end]
            )
            # Load results into memory (don't hold open stream because this
            # can time out due to long running operations below)
            readings = tuple(query())
            LOGGER.debug("Family %s: Retrieved %s readings", family_id,
                         len(readings))

            # Convert from UFO readings to Awesome readings
            readings = (
                maps.reading_to_reading(
                    reading=reading,
                    reading_types=reading_types,
                    awesome_sensors=awesome_sensors
                )
                for reading in readings
            )

            # Iterate over data chunks because the Awesome portal API accepts a
            # maximum number of rows per call.
            for i, chunk in enumerate(utils.iter_chunks(
                    readings, chunk_size=settings.BULK_READINGS_CHUNK_SIZE)):
                # Log every 100 chunks
                if i % 100 == 0:
                    LOGGER.info('Family "%s" Chunk %s', family_id, i)
                # Loop to retry if rate limit exceeded
                while True:
                    try:
                        objects.Reading.store_bulk(session, readings=chunk)
                        break
                    # No more readings, so stop
                    except exceptions.EmptyValueError:
                        break
                    # HTTP error
                    except requests.HTTPError as exc:
                        # HTTP status code 429 too many requests
                        # (server-side rate limit)
                        if exc.response.status_code == http.HTTPStatus.TOO_MANY_REQUESTS:
                            # Wait until the system is ready to accept
                            # further requests
                            retry_after = int(
                                exc.response.headers['retry-after'])
                            LOGGER.info(
                                'Rate limit: sleeping for %s seconds',
                                retry_after)
                            time.sleep(retry_after)  # seconds
                        else:
                            raise

                LOGGER.debug('Bulk stored chunk %s with %s rows', i,
                             len(chunk))

                reading_count += len(chunk)

            # Update bookmark
            bookmarks[family_id] = _end
            LOGGER.info('Saved bookmark for family "%s" at %s', family_id,
                        _end.isoformat())

        # Family sync success
        LOGGER.info('synced %s readings for family "%s"', reading_count,
                    family_id)
        total_reading_count += reading_count

    LOGGER.info("Synced %s readings for %s families", total_reading_count,
                len(families))


def sync_sites(session: http_session.PortalSession, sites: Mapping,
               locations: MutableMapping):
    """
    Convert UFO sites into Awesome locations.

    Create a new location for each site if it doesn't already exist.
    Locations cannot be updated then do nothing.

    :param session: Awesome portal HTTP session
    :param sites: UFO sites
    :param locations: Map of remote Awesome location names to object data
    """

    for site_id, site in sites.items():
        LOGGER.debug("Site '%s': %s", site_id, site)

        # Convert UFO site to Awesome object
        local_location = maps.site_to_location(site)
        LOGGER.debug(local_location)

        # Remote location exists
        if site['name'] in locations:
            # Check for changes
            remote_location = locations[site['name']]
            if maps.is_object_different(local_location, remote_location):
                activity = maps.get_latest_activity(site['activity'])
                # Update existing location
                loc = objects.Location(locations[site['name']]['id'])
                loc.update(session, local_location)
                # Use family name as tag
                loc.add_tag(session, activity['dbh'])

        # No remote location found
        else:
            # Create new location
            body = objects.Location.add(session, local_location)
            new_location = body['data']
            loc = objects.Location(new_location['id'])
            loc.add_tag(session, site['dbh'])

            # Store id of new location
            locations[new_location['name']] = new_location['id']

            LOGGER.info('Created location "%s" from site "%s"',
                        new_location['id'], site_id)


def sync_sensors(session: http_session.PortalSession, sensors: Mapping,
                 awesome_sensors: MutableMapping, locations: Mapping):
    """
    Either update (if changed) or create a new Awesome sensor for each Urban
    Flows sensor. For each sensor, if no changes have been made to the UFO
    sensor metadata then do nothing.

    :param session: Awesome portal HTTP session
    :param sensors: UFO sensors
    :param awesome_sensors: Awesome portal sensors
    :param locations: Map of Awesome location name to object
    """

    # Iterate over UFO sensors
    for sensor_id, sensor in sensors.items():

        # Convert to Awesome object
        local_sensor = maps.sensor_to_sensor(sensor, locations)

        try:
            remote_sensor = awesome_sensors[sensor['name']]

        # Doesn't exist on in Awesome database
        except KeyError:
            # Create new sensor
            body = objects.Sensor.add(session, local_sensor)
            new_sensor = body['data']

            # Store id of new sensor
            awesome_sensors[new_sensor['name']] = new_sensor['id']

            LOGGER.debug('UFO Sensor "%s" => Awesome id %s', sensor_id,
                         new_sensor['id'])

            # Don't update
            continue

        # Have changes been made?
        # Adjust the data structure to match the local object
        remote_sensor['location_id'] = remote_sensor['location']['id']
        if maps.is_object_different(local_sensor, remote_sensor):
            # Update the object on the Awesome portal
            sen = objects.Sensor(remote_sensor['id'])
            sen.update(session, local_sensor)
            LOGGER.debug('UFO Sensor "%s" => Awesome id %s', sensor_id,
                         remote_sensor['location_id'])


def sync_reading_types(session: http_session.PortalSession, detectors: Mapping,
                       reading_types: MutableMapping,
                       remote_reading_category_ids: Mapping,
                       reading_type_groups: list):
    """
    Map local Urban Flows Observatory "detectors" to remote "reading types" on
    the Awesome Portal.

    :param session: Awesome portal HTTP connection
    :param detectors: UFO metrics
    :param reading_types: Awesome metrics
    :param remote_reading_category_ids: Map of reading types to reading
                                        categories
    :param reading_type_groups: The local configuration for groups of reading
                                types
    """
    # Map reading types to reading categories from local configuration file
    # This is the desired end-state configuration to sync to the remote server
    reading_type_name_to_category_ids = maps.reading_type_to_reading_categories(
        reading_type_groups=reading_type_groups,
        awesome_reading_categories=remote_reading_category_ids)

    # Iterate over UF detectors
    for detector_name, detector in detectors.items():

        LOGGER.debug("DETECTOR %s %s", detector_name, detector)

        local_reading_type = maps.detector_to_reading_type(detector)

        try:
            # Does a reading type with this name exist in the database?
            remote_reading_type = reading_types[detector_name]

        # Doesn't exist on in Awesome database
        except KeyError:
            # Create new
            body = objects.ReadingType.add(session, local_reading_type)
            new_reading_type = body['data']
            reading_types[new_reading_type['name']] = new_reading_type
            continue

        # Add/update a reading type
        reading_type = objects.ReadingType(remote_reading_type['id'])
        reading_type.update(session, local_reading_type)

        # Reading categories
        try:
            remote_reading_category_ids = {
                rc['id'] for rc
                in reading_type.get(session)['reading_categories']}
        except KeyError:
            LOGGER.error(reading_type.get(session))
            raise

        try:
            local_reading_category_ids = reading_type_name_to_category_ids[
                detector_name]

        # No reading categories are configured for this reading type
        except KeyError:
            continue

        # Add new reading categories to this reading type
        for reading_category_id in set(local_reading_category_ids) - set(
                remote_reading_category_ids):
            reading_type.add_reading_category(session, reading_category_id)

        # Remove deleted items
        for reading_category_id in set(remote_reading_category_ids) - set(
                local_reading_category_ids):
            reading_type.remove_reading_category(session, reading_category_id)


def sync_reading_categories(session, reading_categories: MutableMapping,
                            reading_type_groups: list):
    """
    Sync reading categories (e.g. "Air Quality" is a category containing
    reading types PM 1, PM 2.5, PM 10.)

    :param session: Awesome portal HTTP session
    :param reading_categories: Map existing Awesome reading category names to
                               their object data
    :param reading_type_groups: Locally configured groups to be synced
    """

    # Iterate over locally-configured items
    for read_cat in reading_type_groups:
        LOGGER.debug('Reading category: %s', read_cat)

        # Build the data to populate the Awesome Reading Category
        local_reading_category = objects.ReadingCategory.new(
            name=read_cat['name'], icon_name=read_cat['icon_name'])

        # Check if this items already exists
        if read_cat['id'] in reading_categories:
            # Update existing reading category
            reading_category = reading_categories[read_cat['name']]
            reading_category = objects.ReadingCategory(reading_category['id'])
            reading_category.update(session, obj=local_reading_category)

        else:
            # Make new reading category
            body = objects.ReadingCategory.add(session, local_reading_category)

            # Update record in memory to keep track of newly-created objects
            new_reading_category = body['data']
            reading_categories[new_reading_category['name']] = \
                new_reading_category['id']


def get_urban_flows_metadata() -> tuple:
    """Retrieve all Urban Flows metadata"""

    metadata = assets.get_metadata()

    detectors = assets.Sensor.get_detectors_from_sensors(metadata['sensors'])

    return metadata['sites'], metadata['families'], metadata['pairs'], \
           metadata['sensors'], detectors


def build_awesome_object_map(session: http_session.PortalSession,
                             cls: Type[objects.AwesomeObject]) -> \
        MutableMapping[str, dict]:
    """
    Map Awesome object names (case insensitive) to the object data
    """
    # Case-insensitive
    return {obj['name'].upper(): obj for obj in cls.list_iter(session)}


def load_json_objects(path: Path) -> List[dict]:
    """
    Load the AQI standards that you want to sync to the remote server.
    """
    with pathlib.Path(path).open() as file:
        return [dict(obj) for obj in json.load(file)]


def sync_aqi_standards(session):
    """
    Assume there's only one AQI standard and sync it.
    """

    # Get first local AQI standard definition
    local_standard = settings.AQI_STANDARDS[0]

    try:
        # Update the existing object
        obj = objects.AQIStandard(settings.AWESOME_AQI_STANDARD_ID)
        obj.update(session, local_standard)
    except requests.exceptions.HTTPError as e:
        # If it doesn't already exist then create it
        if e.response.status_code == http.HTTPStatus.NOT_FOUND:
            obj_data = objects.AQIStandard.new(**local_standard)
            objects.AQIStandard.add(session, obj_data)
        else:
            raise


def sync_aqi_readings(session, families: Mapping, locations: Mapping,
                      end: datetime.datetime = None):
    """
    Upload air quality index data to the remote system.

    :param session: HTTP session for the Awesome portal
    :param families: A list of UFO families
    :param locations: A map of UFO sites to Awesome locations
    :param end: Time range upper bound
    """

    # Persist progress through data set time axis
    bookmarks = cache.Cache('aqi')

    # Iterate over families because of UFO database partitioning
    for family_id, family in families.items():

        # Skip traffic flow data, which cannot produce AQI readings
        if family_id == 'SCC_flow':
            continue

        bookmark = bookmarks.get(family_id,
                                 settings.TIME_START)  # type: datetime.datetime

        # Allow at least x hours of data because some AQI calculations
        # require an certain time period rolling average
        time_buffer = utils.now() - datetime.timedelta(
            **settings.AQI_TIME_BUFFER)
        bookmark = min(bookmark, time_buffer)
        # Start at beginning of day
        bookmark = bookmark.replace(hour=0, minute=0, second=0, microsecond=0)

        LOGGER.info("Family '%s' AQI readings since %s", family_id,
                    bookmark.isoformat())

        # sync to current time
        end = end or datetime.datetime.now(datetime.timezone.utc)

        # Iterate over days (due to source database partition)
        for _start, _end in ufdex.UrbanFlowsQuery.generate_time_periods(
                start=bookmark, end=end, freq=datetime.timedelta(days=1)):
            query = ufdex.UrbanFlowsQuery(time_period=[_start, _end],
                                          families={family_id})
            readings = query()

            data = aqi.operations.transform_ufo_data(readings)

            try:
                # Iterate over sites (because AQI is specified per-site)
                for site_id, df in data.groupby('site.id'):
                    df = df.loc[site_id]

                    aq_index = aqi.operations.calculate_air_quality(df)

                    LOGGER.debug('Site "%s" has %s AQI readings', site_id,
                                 len(aq_index.index))

                    # Upload to Awesome portal
                    location = locations[site_id]

                    aqi_readings = maps.aqi_readings(
                        aq_index,
                        aqi_standard_id=settings.AWESOME_AQI_STANDARD_ID,
                        location_id=location['id'],
                    )

                    # Sync readings (The aqi readings input must be chunked)
                    for i, chunk in enumerate(utils.iter_chunks(
                            aqi_readings,
                            chunk_size=settings.BULK_READINGS_CHUNK_SIZE)
                    ):
                        LOGGER.info(
                            "Bulk store AQI readings chunk %s with %s readings",
                            i, len(chunk))
                        objects.AQIReading.store_bulk(session,
                                                      aqi_readings=chunk)

            # Skip empty data sets
            except KeyError:
                if not data.empty:
                    raise

            # Update bookmark so we don't check this time range again
            bookmarks[family_id] = _end
            LOGGER.info("Updated bookmark: family '%s' to %s", family_id,
                        _end.isoformat())


def sync_families(session, families: Mapping[str, dict],
                  sensor_types: MutableMapping[str, dict]):
    """
    Synchronise UFO sensor families to Awesome sensor types.

    :param session: HTTP session for Awesome portal
    :param families: UFO objects, map of family name to family info
    :param sensor_types: Awesome portal objects, map of sensor type name to
                        sensor type metadata
    """
    # Iterate over UFO families and ensure a sensor type record exists for each
    for family_name, family in families.items():
        LOGGER.debug("Syncing family '%s'", family_name)

        sensor_type = objects.SensorType.new(
            **maps.family_to_sensor_type(family_name=family_name))

        if family_name not in sensor_types:

            try:
                remote_sensor_type = sensor_types[family_name.upper()]
                # Update existing sensor type
                response = objects.SensorType(remote_sensor_type['id']).update(
                    session, sensor_type)
                new_sensor_type = response.json()['data']
                LOGGER.debug("Updated sensor type %s", new_sensor_type)

            except KeyError:
                # Add new item
                new_sensor_type = objects.SensorType.add(session, sensor_type)[
                    'data']
                LOGGER.info("Added sensor type %s", new_sensor_type)

            # Update record to keep track of newly-created objects
            sensor_types[family_name] = new_sensor_type

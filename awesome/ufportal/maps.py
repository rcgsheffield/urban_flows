"""
Map Urban Flows assets to Awesome portal objects.
"""


def site_to_location(site: dict) -> dict:
    """Map Urban Flows site to an Awesome portal location"""

    # Get latest activity
    activity = sorted(site['activity'], key=lambda act: act['t0'])[0]

    return dict(
        name=str(site['name']),
        lat=float(site['latitude']),
        lon=float(site['longitude']),
        elevation=int(activity['heightAboveSL']),
    )


def sensor_to_sensor(sensor: dict, locations: dict) -> dict:
    # Get latest site deployment
    pair = sorted(sensor['attachedTo'], key=lambda pair: pair['from'])[0]
    site_name = pair['site']

    # Get location identifier
    location_id = locations[site_name]

    return dict(
        name=str(sensor['name']),
        location_id=location_id,
        sensor_type_id=1,
        active=bool(sensor['isActive'])
    )

import logging
import getpass
import random

import objects
import assets
import maps
import sync
import http_session

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    session = http_session.PortalSession(token=getpass.getpass(
        'Awesome token: '))

    metadata = assets.get_metadata()
    sites = metadata['sites']

    for site_id, site in sites.items():
        print('Site id', site_id, ', name', site['name'])

        site_to_loc = sync.build_awesome_object_map(session, objects.Location)

        location_id = site_to_loc[site_id]['id']

        location = objects.Location(location_id)
        remote_location = location.get(session)

        print('Site', site)

        local_location = maps.site_to_location(site)

        print('Local location', local_location)
        print('Remote location', remote_location)

        is_diff = maps.is_object_different(local_location, remote_location)
        print('Different?', is_diff)

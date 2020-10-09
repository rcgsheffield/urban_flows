import logging
import sync
import http_session
import objects

logging.basicConfig(level=logging.DEBUG)

sites, _, _, _, _ = sync.get_urban_flows_metadata()

session = http_session.PortalSession()

locations = sync.build_awesome_object_map(session, objects.Location)
sync.sync_sites(session, sites, locations=locations)

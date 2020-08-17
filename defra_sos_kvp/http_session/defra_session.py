import logging
import urllib.parse

import requests

import settings

LOGGER = logging.getLogger(__name__)


class DefraMetaSession(requests.Session):
    """
    Metadata about the DEFRA air quality systems
    """

    BASE_URL = 'https://uk-air.defra.gov.uk/data/API/'

    def __init__(self):
        super().__init__()
        self.headers.update({'User-Agent': settings.USER_AGENT})

    def request(self, *args, **kwargs):
        response = super().request(*args, **kwargs)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            LOGGER.error(response.text)
            raise
        return response

    def call(self, endpoint: str, **kwargs):
        url = urllib.parse.urljoin(self.BASE_URL, endpoint)
        response = self.get(url, **kwargs)
        return response.json()

    @property
    def regions(self) -> dict:
        _regions = self.call('local-authority-region')['government_region']

        regions = dict()

        # Parse data types
        for key, value in _regions.items():
            try:
                key = int(key)
                value['region_id'] = int(value['region_id'])
                regions[key] = value

            # Ignore redundant nested values
            except ValueError:
                pass

        return regions

    @property
    def groups(self) -> dict:
        return self.call('group')

    def site_processes(self, region_id: int, group_id: int) -> list:
        params = dict(group_id=group_id, region_id=region_id)
        return self.call('site-process-featureofinterest-by-region', params=params)

    def get_sites_by_region(self, region_id: int) -> iter:
        for group_id, group in self.groups.items():
            LOGGER.info("Group %s: %s", group_id, group[0])

            for site in self.site_processes(region_id, group_id=group_id):
                LOGGER.debug("Site %s %s", site['site_name'], site['station_identifier'])
                yield site

    @staticmethod
    def point_within_bbox(point: tuple, bbox: list) -> bool:
        """Check if a point is within a bounding box (GeoJSON format)"""
        longitude, latitude = point

        # Unpack GeoJSON format
        bbox = bbox[0]

        # Validate shape
        if bbox[0] != bbox[4]:
            raise ValueError("Bounding box is not a closed polygon")

        # Get corners of rectangle
        bottom_left, _, top_right, _, _ = bbox

        return bottom_left[0] <= longitude <= top_right[0] and bottom_left[1] <= latitude <= top_right[1]

    @classmethod
    def spatial_filter(cls, sites: iter, bounding_box: list) -> iter:
        """
        Filter sites using a longitude-latitude bounding box

        :param sites: A collection of sensor stations
        :param bounding_box: GeoJSON bounding box
        """
        for site in sites:

            point = float(site['longitude']), float(site['latitude'])
            if DefraMetaSession.point_within_bbox(point, bounding_box):
                yield site

    def get_sampling_points_by_region(self, region_id: int) -> iter:
        for site in self.get_sites_by_region(region_id=region_id):
            yield from self.get_site_sampling_points(site)

    @classmethod
    def get_site_sampling_points(cls, site: dict) -> iter:
        """Get all the sampling points from a site"""
        for parameter in site['parameter_ids']:
            yield parameter['sampling_point']

    @classmethod
    def get_site_sampling_features(cls, site: dict) -> iter:
        """Get all the sampling features from a site"""
        for parameter in site['parameter_ids']:
            for feature_of_interest in parameter['feature_of_interest']:
                sampling_feature = feature_of_interest['featureOfInterset']

                # Skip missing values
                if sampling_feature == 'missingFOI':
                    continue

                yield sampling_feature

    def get_features_of_interest_by_region(self, region_id: int) -> set:
        sampling_features = set()

        for site in self.get_sites_by_region(region_id=region_id):
            sampling_features.update(self.get_site_sampling_features(site))

        return sampling_features

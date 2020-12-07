from typing import Dict, List


class FingertipObject:
    BASE_URL = 'https://fingertips.phe.org.uk/api'
    EDGE = ''

    @classmethod
    def build_url(cls, endpoint: str) -> str:
        return "{}/{}".format(cls.BASE_URL, endpoint)

    @classmethod
    def list(cls, session, **kwargs):
        url = cls.build_url(cls.EDGE)
        return session.call(url, **kwargs)


class Profile(FingertipObject):
    EDGE = 'area_types'


class AreaType(FingertipObject):
    EDGE = 'area_types'


class AreaCategory(FingertipObject):
    EDGE = 'area_categories'


class Indicator(FingertipObject):
    EDGE = 'indicator_metadata/all'

    @classmethod
    def search(cls, session, search_text: str, **kwargs) -> Dict[int, List[int]]:
        """
        Words can be combined with AND / OR

        Returns a hash of area type IDs that each map to a list of IDs of indicators for which the metadata matches the
        search text.
        """
        url = cls.build_url('indicator_search')
        params = dict(search_text=search_text, **kwargs.get('params', dict()))
        return session.call(url, params=params, **kwargs)


class Data(FingertipObject):
    EDGE = 'available_data'

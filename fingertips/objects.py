from typing import Dict, List, Iterable


class FingertipObject:
    """
    Public Health England Fingertips API object

    See docs: https://fingertips.phe.org.uk/api/
    """
    BASE_URL = 'https://fingertips.phe.org.uk/api'
    EDGE = ''

    def __init__(self, identifier: int):
        self.identifier = identifier

    @classmethod
    def build_url(cls, endpoint: str) -> str:
        return "{}/{}".format(cls.BASE_URL, endpoint)

    @classmethod
    def list(cls, session, **kwargs):
        url = cls.build_url(cls.EDGE)
        return session.call(url, **kwargs)

    @staticmethod
    def bool(b: bool) -> str:
        return 'yes' if b else 'no'

    @staticmethod
    def cat(items: Iterable, delimiter: str = ',') -> str:
        """
        Build comma-separated list
        """
        # Convert all items to strings
        return delimiter.join((str(x) for x in items))


class Profile(FingertipObject):
    """
    Collections of data sets. It contains groups of data (the tabs on the GUI display.)
    """
    EDGE = 'profiles'

    def get(self, session) -> dict:
        return session.call(self.build_url('profile'), params=dict(profile_id=self.identifier))


class Group(FingertipObject):
    """
    A group of indicators within a profile
    """
    EDGE = 'group_metadata'

    def get(self, session):
        return self.list(session, group_ids={self.identifier})

    @classmethod
    def list(cls, session, group_ids: Iterable[int], **kwargs):
        return super().list(session, params=dict(group_ids=cls.cat(group_ids)), **kwargs)

    def indicators(self, session, **kwargs):
        return Indicator.by_group_id(session=session, group_ids={self.identifier}, **kwargs)


class AreaType(FingertipObject):
    EDGE = 'area_types'


class AreaCategory(FingertipObject):
    EDGE = 'area_categories'


class Indicator(FingertipObject):
    """
    A quantitative metric such as life expectancy or hospital admissions.
    """
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

    @classmethod
    def by_group_id(cls, session, group_ids: Iterable[int], include_definition: bool = False,
                    include_system_content: bool = False):
        return session.call(cls.build_url('indicator_metadata/by_group_id'),
                            params=dict(group_ids=cls.cat(group_ids),
                                        include_definition=cls.bool(include_definition),
                                        include_system_content=cls.bool(include_system_content),
                                        )
                            )

    @classmethod
    def list(cls, session, indicator_ids, restrict_to_profile_ids: set = None, include_definition: bool = False,
             include_system_content: bool = False, **kwargs):
        return session.call(cls.build_url('indicator_metadata/by_indicator_id'), params=dict(
            indicator_ids=cls.cat(indicator_ids),
            restrict_to_profile_ids=cls.cat(restrict_to_profile_ids or set()),
            include_definition=cls.bool(include_definition),
            include_system_content=cls.bool(include_system_content),
        ), **kwargs)

    def get(self, session):
        return self.list(session, indicator_ids={self.identifier})


class Data(FingertipObject):
    EDGE = 'available_data'

from typing import Dict, List, Iterable, Set


class FingertipObject:
    """
    Public Health England Fingertips API object

    See docs: https://fingertips.phe.org.uk/api/
    """
    BASE_URL = 'https://fingertips.phe.org.uk/api'
    EDGE = str()

    def __init__(self, identifier: int):
        self.identifier = identifier

    @classmethod
    def build_url(cls, endpoint: str) -> str:
        return "{}/{}".format(cls.BASE_URL, endpoint)

    @classmethod
    def list(cls, session, **params) -> List[dict]:
        url = cls.build_url(cls.EDGE)
        return session.call(url, params=params)

    @staticmethod
    def bool(b: bool) -> str:
        return 'yes' if b else 'no'

    @staticmethod
    def cat(items: Iterable = None, delimiter: str = ',') -> str:
        """
        Build comma-separated list
        """
        # Default to empty collection
        items = items or tuple()
        # Convert all items to strings
        return delimiter.join((str(x) for x in items))

    def get(self, session) -> dict:
        """
        Retrieve the data representing this object.
        :param session: HTTP transport
        :return: Object data
        """
        raise NotImplementedError

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.identifier)


class Profile(FingertipObject):
    """
    National Public Health Profiles are a source of indicators across a
    range of health themes. More info at https://fingertips.phe.org.uk

    These are data marts (collections of data sets with common dimensions). It contains groups of data (the tabs on the
    GUI display.) For example, the profile with identifier 100 is "Wider Impacts of COVID-19 on Health."
    """
    EDGE = 'profiles'

    def get(self, session) -> dict:
        return session.call(self.build_url('profile'), params=dict(profile_id=self.identifier))

    def area_types(self, session):
        """
        Get the area types used in this health profile.
        """
        return AreaType.list(session, profile_ids={self.identifier})


class Group(FingertipObject):
    """
    A group of indicators within a profile
    """
    EDGE = 'group_metadata'

    def get(self, session):
        return self.list(session, group_ids={self.identifier})

    @classmethod
    def list(cls, session, group_ids: Iterable[int], **params):
        return super().list(session, group_ids=cls.cat(group_ids), **params)

    def indicators(self, session, **kwargs):
        return Indicator.by_group_id(session=session, group_ids={self.identifier}, **kwargs)


class AreaType(FingertipObject):
    """
    Geographical systems e.g. categories governmental regions, etc.

    For example: Area type 201 is "Lower tier local authorities (4/19 - 3/20)"
    """
    EDGE = 'area_types'

    @classmethod
    def list(cls, session, profile_ids: Set[int] = None, **params):
        return super().list(session, profile_ids=cls.cat(profile_ids), **params)

    def areas(self, session, **kwargs):
        """

        :param session:
        :return:
        """
        return Area.list(session, area_type_id=self.identifier, **kwargs)


class Area(FingertipObject):
    """
    A specific geospatial 2D place e.g. "Sheffield"
    """
    EDGE = 'areas/by_area_type'

    def list(self, session, area_type_id: int, profile_id: int = None, template_profile_id: int = None,
             retrieve_ignored_areas: bool = False):
        """
        Get a list of areas of a specific area type

        https://fingertips.phe.org.uk/api#!/Areas/Areas_GetAreasOfAreaType
        """
        return super().list(session, area_type_id=area_type_id, profile_id=profile_id,
                            template_profile_id=template_profile_id, retrieve_ignored_areas=retrieve_ignored_areas)


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
    def list(cls, session, indicator_ids: Set[int] = None, restrict_to_profile_ids: Set[int] = None,
             include_definition: bool = False, include_system_content: bool = False, **params):
        params = dict(
            indicator_ids=cls.cat(indicator_ids),
            restrict_to_profile_ids=cls.cat(restrict_to_profile_ids),
            include_definition=cls.bool(include_definition),
            include_system_content=cls.bool(include_system_content),
            **params,
        )
        return session.call(cls.build_url('indicator_metadata/by_indicator_id'), params=params)

    def get(self, session):
        return self.list(session, indicator_ids={self.identifier})

    def data(self, session, **kwargs):
        return Data.by_indicator_id(session, indicator_ids={self.identifier}, **kwargs)


class Data(FingertipObject):
    """
    https://fingertips.phe.org.uk/api#/Data
    """
    EDGE = 'available_data'

    @classmethod
    def by_indicator_id(cls, session, indicator_ids: Set[int], child_area_type_id: int, parent_area_type_id: int,
                        profile_id: int = None, parent_area_code: str = None):
        """
        https://fingertips.phe.org.uk/api#!/Data/Data_GetDataFileForIndicatorList
        """
        params = dict(
            indicator_ids=cls.cat(indicator_ids),
            child_area_type_id=child_area_type_id,
            parent_area_type_id=parent_area_type_id,
            profile_id=profile_id,
            parent_area_code=parent_area_code,
        )
        return session.call(cls.build_url('all_data/csv/by_indicator_id'), params=params)

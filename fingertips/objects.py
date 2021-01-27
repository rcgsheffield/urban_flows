from typing import Dict, List, Iterable, Set

import utils


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


class ProfileGroup(FingertipObject):
    EDGE = 'group_metadata'

    @classmethod
    def list(cls, session, group_ids: Iterable[int]):
        super().list(session, group_ids=cls.cat(group_ids))


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

    def data(self, session, **kwargs):
        return Data.by_profile_id(session, profile_id=self.identifier, **kwargs)

    def parent_area_types(self, session):
        return AreaType.parent_area_types(session, profile_id=self.identifier)

    @classmethod
    def containing_indicators(cls, session, indicator_ids: Set[int], area_type_id: int = None) -> Dict[int, List[dict]]:
        """
        Find all the profiles containing these indicators.

        :returns: A dictionary of indicator ID to a list of profiles
        """
        # https://fingertips.phe.org.uk/api#!/Profiles/Profiles_GetProfilesPerIndicator
        params = dict(indicator_ids=cls.cat(indicator_ids), area_type_id=area_type_id)
        return session.call(cls.build_url('profiles_containing_indicators'), params=params)


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
        return Area.list(session, area_type_id=self.identifier, **kwargs)

    def get(self, session) -> dict:
        for area_type in self.list(session):
            if area_type['Id'] == self.identifier:
                return area_type
        raise ValueError("Area type not found")

    @classmethod
    def parent_area_types(cls, session, profile_id: int = None, template_profile_id: int = None) -> List[dict]:
        """
        Returns a list of area types each with a list of available parent area types
        """
        # https://fingertips.phe.org.uk/api#!/Areas/Areas_GetAreaTypesWithParentAreaTypes
        params = dict(profile_id=profile_id, template_profile_id=template_profile_id)
        return session.call(cls.build_url('area_types/parent_area_types'), params=params)

    def indicators(self, session):
        """
        Get the indicators available for this area type
        """
        return Data.available_data(session, area_type_id=self.identifier)


class Area(FingertipObject):
    """
    A specific geospatial 2D place e.g. "Sheffield"
    """
    EDGE = 'areas/by_area_type'

    @classmethod
    def list(cls, session, area_type_id: int, profile_id: int = None, template_profile_id: int = None,
             retrieve_ignored_areas: bool = False):
        """
        Get a list of areas of a specific area type

        https://fingertips.phe.org.uk/api#!/Areas/Areas_GetAreasOfAreaType
        """
        return super().list(session, area_type_id=area_type_id, profile_id=profile_id,
                            template_profile_id=template_profile_id, retrieve_ignored_areas=retrieve_ignored_areas)

    def address(self, session):
        area = self.get(session)
        return session.call('area_address', params=dict(area_code=area['Code']))


class Indicator(FingertipObject):
    """
    A quantitative metric such as life expectancy or hospital admissions.
    """
    EDGE = 'indicator_metadata/all'

    @classmethod
    def search(cls, session, search_text: str, restrict_to_profile_ids: Set[int]) -> Dict[int, List[int]]:
        """
        Words can be combined with AND / OR

        Returns a hash of area type IDs that each map to a list of IDs of indicators for which the metadata matches the
        search text.
        """
        # https://fingertips.phe.org.uk/api#!/IndicatorMetadata/IndicatorMetadata_GetIndicatorsThatMatchTextByAreaTypeId
        params = dict(search_text=search_text, restrict_to_profile_ids=cls.cat(restrict_to_profile_ids))
        return session.call(cls.build_url('indicator_search'), params=params)

    @classmethod
    def search_list(cls, session, search_text: str) -> List[dict]:
        """
        Words can be combined with AND / OR

        Returns a list of the indicators in the order of how well they match the search text.
        """
        # https://fingertips.phe.org.uk/api#!/IndicatorMetadata/IndicatorMetadata_GetIndicatorsThatMatchTextAsList
        return session.call(cls.build_url('indicator_search_list_indicators'), params=dict(search_text=search_text))

    @classmethod
    def by_group_id(cls, session, group_ids: Iterable[int], include_definition: bool = False,
                    include_system_content: bool = False):
        params = dict(
            group_ids=cls.cat(group_ids),
            include_definition=cls.bool(include_definition),
            include_system_content=cls.bool(include_system_content),
        )
        return session.call(cls.build_url('indicator_metadata/by_group_id'), params=params)

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

    def area_types(self, session):
        """
        Get area types available for this indicator
        """
        return Data.available_data(session, indicator_id=self.identifier)


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

        :param child_area_type_id: Area type
        :param parent_area_type_id: Areas grouped by
        """
        params = dict(
            indicator_ids=cls.cat(indicator_ids),
            child_area_type_id=child_area_type_id,
            parent_area_type_id=parent_area_type_id,
            profile_id=profile_id,
            parent_area_code=parent_area_code,
        )
        yield from session.call_iter(cls.build_url('all_data/csv/by_indicator_id'), params=params)

    @classmethod
    def by_profile_id(cls, session, child_area_type_id: int, parent_area_type_id: int, profile_id: int,
                      parent_area_code: str = None):
        params = dict(
            child_area_type_id=child_area_type_id,
            parent_area_type_id=parent_area_type_id,
            profile_id=profile_id,
            parent_area_code=parent_area_code,
        )
        yield from session.call_iter(cls.build_url('all_data/csv/by_profile_id'), params=params)

    @classmethod
    def available_data(cls, session, indicator_id: int = None, area_type_id: int = None):
        """
        Get the area types that are available for each indicator, or the indicators that are available for each area
        type.

        If only the indicator ID is specified then the results will be returned for every area type for which data is
        available.
        """
        # https://fingertips.phe.org.uk/api#!/Data/Data_GetAvailableDataForGrouping
        return session.call('available_data', params=dict(indicator_id=indicator_id, area_type_id=area_type_id))


class AreaCategory(FingertipObject):
    EDGE = 'area_categories'


class Category(FingertipObject):
    EDGE = 'categories'

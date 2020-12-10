from typing import List


class KCANObject:
    """
    KCAN API Object
    https://docs.ckan.org/en/2.7/api/index.html
    """

    def __init__(self, identifier: str):
        self.id = identifier


class Package(KCANObject):
    """
    KCAN Package (data set)
    """

    @classmethod
    def list(cls, session, limit: int = None, offset: int = None) -> List[str]:
        """
        https://docs.ckan.org/en/2.7/api/index.html#ckan.logic.action.get.package_list
        """
        return session.call('package_list', params=dict(limit=limit, offset=offset))

    @classmethod
    def show(cls, session, identifier: str, use_default_schema: bool = False, include_tracking: bool = False):
        """
        Return the metadata of a dataset (package) and its resources.
        https://docs.ckan.org/en/2.7/api/index.html#ckan.logic.action.get.package_show
        """
        return session.call('package_show', params=dict(id=identifier))

    def get(self, session):
        self.show(session=session, identifier=self.id)


class Tag(KCANObject):

    @classmethod
    def list(cls, session):
        return session.call('tag_list')

from typing import List


class KCANObject:
    """
    KCAN API Object
    https://docs.ckan.org/en/2.7/api/index.html

    API reference
    https://docs.ckan.org/en/2.7/api/index.html#action-api-reference
    """

    def __init__(self, identifier: str):
        self.id = identifier
        self.data = dict()

    def get(self, session) -> dict:
        self.data = self.show(session=session, id=self.id)
        return self.data

    @classmethod
    def build_endpoint(cls, action: str) -> str:
        return "{class_name}_{action}".format(class_name=cls.__name__, action=action).casefold()

    @classmethod
    def list(cls, session, **params) -> List[str]:
        return session.call(cls.build_endpoint('list'), params=params)

    @classmethod
    def show(cls, session, **params):
        return session.call(cls.build_endpoint('show'), params=params)

    @classmethod
    def search(cls, session, **params) -> dict:
        """
        https://docs.ckan.org/en/2.7/api/index.html#ckan.logic.action.get.package_search
        """
        return session.call(cls.build_endpoint('search'), params=params)


class Package(KCANObject):
    """
    KCAN Package (data set)
    """

    @property
    def name(self) -> str:
        return self.data['name']


class Tag(KCANObject):
    pass


class Organisation(KCANObject):
    pass

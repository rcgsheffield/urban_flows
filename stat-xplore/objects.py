from typing import List


class StatObject:
    EDGE = str()

    def __init__(self, identifier: str):
        self.identifier = identifier

    @classmethod
    def urljoin(cls, *args) -> str:
        return '/'.join((cls.EDGE, *args))

    @classmethod
    def list(cls, session, **params):
        return session.call(cls.EDGE, params=params)

    @classmethod
    def show(cls, session, identifier, **params) -> dict:
        return session.call(cls.urljoin(identifier), params=params)

    def get(self, session, **params) -> dict:
        return self.show(session, self.identifier, params=params)


class Schema(StatObject):
    EDGE = 'schema'


class Table(StatObject):
    EDGE = 'table'

    def query(self, session, measures: List[str], dimensions: List[list], recodes: dict = None, **params) -> dict:
        """
        The /table endpoint allows you to submit table queries and receive the results.

        https://stat-xplore.dwp.gov.uk/webapi/online-help/Open-Data-API-Table.html
        """
        request_body = dict(
            database=self.identifier,
            measures=measures,
            recodes=recodes,
            dimensions=dimensions,
        )
        return session.call('POST', self.EDGE, json=request_body, params=params)

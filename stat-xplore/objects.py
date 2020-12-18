import json
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

    @classmethod
    def query(cls, session, measures: List[str], dimensions: List[list], database: str, recodes: dict = None,
              **params) -> dict:
        """
        The /table endpoint allows you to submit table queries and receive the results.

        https://stat-xplore.dwp.gov.uk/webapi/online-help/Open-Data-API-Table.html

        To generate query JSON: https://stackoverflow.com/a/65341265/8634200
        """
        request_body = dict(
            database=database,
            measures=measures,
            recodes=recodes,
            dimensions=dimensions,
        )
        return session.call(cls.EDGE, method='POST', json=request_body, params=params)

    @classmethod
    def query_json(cls, session, query: str, **params) -> dict:
        query_dict = dict(json.loads(query))
        return cls.query(session=session, **query_dict, **params)

    def run_query(self, session, **kwargs):
        return self.query(session=session, database=self.identifier, **kwargs)

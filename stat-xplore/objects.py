class StatObject:
    EDGE = str()

    def __init__(self, identifier: str):
        self.identifier = identifier

    @classmethod
    def urljoin(cls, *args) -> str:
        return '/'.join((cls.EDGE, *args))

    @classmethod
    def list(cls, session):
        return session.call(cls.EDGE)

    @classmethod
    def show(cls, session, identifier: str) -> dict:
        return session.call(cls.urljoin(identifier))

    def get(self, session) -> dict:
        return self.show(session, self.identifier)


class Schema(StatObject):
    EDGE = 'schema'


class Table(StatObject):
    EDGE = 'table'

    def show(self, session, identifier, measures: list, **kwargs) -> dict:
        """
        The /table endpoint allows you to submit table queries and receive the results.

        https://stat-xplore.dwp.gov.uk/webapi/online-help/Open-Data-API-Table.html
        """
        request = dict(
            database=identifier,
            measures=list(measures or list())
        )
        return session.call(self.EDGE, json=request)

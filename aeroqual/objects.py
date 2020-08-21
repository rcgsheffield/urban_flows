import urllib.parse

from http_session import AeroqualSession


class Object:
    EDGE = None

    def __init__(self, identifier: str):
        self.identifier = identifier

    @classmethod
    def list(cls, session: AeroqualSession):
        return session.call(endpoint=cls.EDGE)

    def get(self, session: AeroqualSession):
        return session.call(self.endpoint)

    @property
    def endpoint(self) -> str:
        return urllib.parse.urljoin(self.EDGE, self.identifier)


class Instrument(Object):
    EDGE = 'instrument'

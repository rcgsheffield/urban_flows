from http_session import AeroqualSession


class Object:
    EDGE = None

    def __init__(self, identifier: str):
        self.identifier = identifier

    @classmethod
    def list(cls, session: AeroqualSession, **kwargs):
        return session.call(endpoint=cls.EDGE)

    def get(self, session: AeroqualSession, **kwargs):
        return session.call(self.endpoint, **kwargs)

    @property
    def endpoint(self) -> str:
        return "{}/{}".format(self.EDGE, self.identifier)


class Instrument(Object):
    EDGE = 'instrument'


class Data(Object):
    EDGE = 'data'

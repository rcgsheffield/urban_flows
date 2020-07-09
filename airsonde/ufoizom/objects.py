from datetime import datetime, timedelta


class OizomObject:
    EDGE = ''

    @classmethod
    def call(cls, session, endpoint, **kwargs):
        return session.call(cls.build_endpoint(cls.EDGE, endpoint), **kwargs)

    @staticmethod
    def build_endpoint(*parts):
        return '/'.join(parts)

    @classmethod
    def list(cls, session):
        return session.call(cls.EDGE)


class Device(OizomObject):
    EDGE = 'devices'

    @classmethod
    def status(cls, session):
        return cls.call(session, 'status')

    @classmethod
    def calibration(cls, session):
        return cls.call(session, 'calibaration')  # sic

    @classmethod
    def get_device(cls, session, device_id):
        return cls.call(session, device_id)

    @classmethod
    def get_device_status(cls, session, device_id):
        return cls.call(session, cls.build_endpoint(device_id, 'status'))


class Data(OizomObject):
    EDGE = 'data'

    @classmethod
    def current(cls, session):
        return cls.call(session, 'cur')[0]

    @classmethod
    def current_for_device(cls, session, device_id):
        return cls.call(session, cls.build_endpoint('cur', device_id))[0]

    @classmethod
    def _analytics(cls, session, device_id, gte: int, lte: int, avg: int):
        return cls.call(session, cls.build_endpoint('analytics', device_id), params=dict(gte=gte, lte=lte, avg=avg))

    @classmethod
    def analytics(cls, session, device_id, start: datetime, end: datetime, average: timedelta):
        gte = int(start.timestamp())
        lte = int(end.timestamp())
        avg = int(average.total_seconds())
        return cls._analytics(session, device_id, gte, lte, avg)


class Alert(OizomObject):
    EDGE = 'alerts'


class AlertConfig(OizomObject):
    EDGE = 'alertconfigs'


class Parameter(OizomObject):
    EDGE = 'parameters'


class DeviceType(OizomObject):
    EDGE = 'devicetypes'

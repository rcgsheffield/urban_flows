"""
The Things Network Data Storage objects
"""


class Device:

    def __init__(self, device_id):
        self.device_id = device_id

    @classmethod
    def list(cls, session) -> list:
        """
        List devices identifier strings in the database.

        Warning: devices that haven't sent any data won't appear in this list.

        https://mj-ttgopaxcounter.data.thethingsnetwork.org/#/devices

        :rtype: list[str]
        """
        return session.call('devices')

    @classmethod
    def run_query(cls, session, device_id: str, last: str = None):
        endpoint = "query/{}".format(device_id)
        return session.call(endpoint, params=dict(last=last))

    def query(self, session, last: str = None):
        return self.run_query(session, device_id=self.device_id, last=last)

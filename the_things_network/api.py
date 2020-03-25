class Query:
    def __call__(self, last: str, session):
        """
        https://mj-ttgopaxcounter.data.thethingsnetwork.org/#!/query/get_api_v2_query

        :param last: Duration on which we want to get the data (default 1h). Pass 30s for the last 30 seconds, 1h for
                     the last hour, 2d for the last 48 hours, etc
        :return: A collection of data points
        """
        return session.call('query', params=dict(last=last))


class Device:

    def __init__(self, device_id):
        self.device_id = device_id

    @classmethod
    def list(cls, session) -> list:
        """
        https://mj-ttgopaxcounter.data.thethingsnetwork.org/#/devices

        :rtype: list[str]
        """
        return session.call('devices')

    @classmethod
    def run_query(cls, session, device_id: str, last: str = None):
        endpoint = f"query/{device_id}"
        return session.call(endpoint, params=dict(last=last))

    def query(self, session, last: str = None):
        return self.run_query(session, device_id=self.device_id, last=last)

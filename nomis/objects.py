from typing import List


class NomisObject:
    def __init__(self, identifier: str):
        self.id = identifier
        self.data = None


class KeyFamily(NomisObject):
    """
    Nomis data set
    """

    @classmethod
    def list(cls, session, search: str = None):
        """
        Discover available datasets

        Get a JSON file with "keyfamilies" variable, containing an array of "keyfamily" nodes
        """
        # /api/v01/dataset/def.sdmx.json
        data = session.call('dataset/def.sdmx.json', params=dict(search=search))
        return data['structure']['keyfamilies']['keyfamily']

    def get(self, session) -> dict:
        """
        Use the "id" attribute from one of the variables to get the structure of an individual dataset, in this case the
        "Jobseeker's Allowance with Rates and Proportions" dataset
        """
        # /api/v01/dataset/NM_1_1/def.sdmx.json
        self.data = session.call('dataset/{id}/def.sdmx.json'.format(id=self.id))
        return self.key_family

    @property
    def key_family(self):
        return self.data['keyfamilies']['keyfamily'][0]

    @property
    def components(self):
        return self.data

    @property
    def dimensions(self) -> List[dict]:
        raise NotImplementedError
        # return self.key_family['dimension']

    @property
    def params(self) -> dict:
        raise NotImplementedError

import os.path
import urllib.parse
import xml.etree.ElementTree


class SpatialObject:
    """
    Defra's Air Quality Spatial Object Register (Beta release)

    https://uk-air.defra.gov.uk/data/so/about/
    """

    DIR = 'spatial_objects'
    BASE_URL = 'https://uk-air.defra.gov.uk/data/so/'

    def __init__(self, url: str):
        self.url = url
        self.latitude = None
        self.longitude = None
        self.inlet_height = None
        self.data = self.load()

        self.root = xml.etree.ElementTree.fromstring(self.data)
        self.parse()

    def load(self, session):
        """Load XML data"""

        # Get meta-data
        try:
            # Load data
            with open(self.path) as file:
                data = file.read()

        except FileNotFoundError:
            # Download data
            data = self.get(session)

            # Save to disk
            with open(self.path, 'x') as file:
                file.write(data.decode())

        return data

    def get(self, session):
        return session.get(self.url, params=dict(format='application/xml')).content

    @property
    def filename(self):
        return "{}.xml".format(self.name)

    @property
    def path(self):
        return os.path.join(self.DIR, self.filename)

    @property
    def name(self):
        return urllib.parse.urlsplit(self.url).path.split('/')[-1]

    def parse(self):
        """Read the properties from the XML file"""

        for elem in self.root[0][0]:

            # Geographical location
            if elem.tag == '{http://www.opengis.net/samplingSpatial/2.0}shape':
                point = elem[0]

                if point.tag != '{http://www.opengis.net/gml/3.2}Point':
                    raise ValueError(point.tag)

                self.latitude, self.longitude = (float(s) for s in point[0].text.split())

            elif elem.tag == '{http://dd.eionet.europa.eu/schemaset/id2011850eu-1.0}inletHeight':
                self.inlet_height = float(elem.text)

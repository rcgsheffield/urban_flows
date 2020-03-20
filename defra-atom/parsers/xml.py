import xml.etree.ElementTree


class XMLParser:
    """
    XML Parser
    """

    XLINK_HREF = '{http://www.w3.org/1999/xlink}href'
    XLINK_TITLE = '{http://www.w3.org/1999/xlink}title'

    NAMESPACE_MAP = dict()

    def __init__(self, root):
        try:
            self.root = self.parse(root)
        except TypeError:
            self.root = root

        self.url = None

    @classmethod
    def parse(cls, data: str):
        """Parse XML document"""
        return xml.etree.ElementTree.fromstring(data)

    def __iter__(self):
        yield from self.root

    def findall_within(self, elem: xml.etree.ElementTree.Element, match: str):
        return elem.findall(match, namespaces=self.NAMESPACE_MAP)

    def findall(self, match: str):
        return self.findall_within(self.root, match)

    def find_within(self, elem: xml.etree.ElementTree.Element, match: str):
        return elem.find(match, namespaces=self.NAMESPACE_MAP)

    def find(self, match: str):
        return self.find_within(self.root, match)

    @classmethod
    def get(cls, session, url, **kwargs):
        """Download data and initialise object"""

        data = session.get(url, **kwargs).content
        obj = cls(data)
        obj.url = url

        return obj

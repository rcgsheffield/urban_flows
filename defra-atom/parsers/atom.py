import parsers.xml


class AtomParser(parsers.xml.XMLParser):
    """
    Atom feed parser
    """

    NAMESPACE_MAP = dict(
        atom='http://www.w3.org/2005/Atom',
        georss='http://www.georss.org/georss',
    )

    @property
    def entries(self) -> list:
        return [Entry(elem) for elem in self.findall('atom:entry')]


class Entry(AtomParser):
    """
    Atom Entry
    """

    @property
    def id(self) -> str:
        return self.find('atom:id').text.strip()

    @property
    def alternate_links(self) -> list:
        links = self.findall("atom:link[@rel='alternate']")
        return [link.attrib for link in links]

import logging

import pandasdmx
import pandasdmx.reader

LOGGER = logging.getLogger(__name__)

# https://www.nomisweb.co.uk/api/v01/dataset/NM_1_1/summary?geography=2092957697&sex=5
SOURCE = {
    "id": "NOMIS",
    "documentation": "https://www.nomisweb.co.uk/api/v01/help",
    "url": "https://www.nomisweb.co.uk/api/v01",
    "name": "Nomis",
    "supported": {"codelist": True, "preview": False}
}


def main():
    logging.basicConfig(level=logging.DEBUG)

    pandasdmx.add_source(SOURCE)
    # source = pandasdmx.source.Source(**SOURCE)

    # pandasdmx.Resource
    #
    # request = pandasdmx.Request(source='NOMIS')
    #
    # LOGGER.debug(request.source)
    #
    # response = request.datastructure('NM_1_1')
    #
    # print(response)

    objt = pandasdmx.read_url('https://www.nomisweb.co.uk/api/v01/dataset/def.sdmx.xml')

    print(repr(objt))
    print(objt)


if __name__ == '__main__':
    main()

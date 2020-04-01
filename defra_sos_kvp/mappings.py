"""
Map European Environment Agency metrics to Urban Observatory metadata codes
"""

UNIT_MAP = {
    # Micrograms per cubic metre
    'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ug.m-3': 'ug/m3',

    # Nanograms per cubic metre
    'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ng.m-3': 'ng/m3',
}

OBSERVED_PROPERTY_MAP = {
    # Particulate matter < 10 µm (aerosol)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5': 'AQ_PM10',

    # Volatile PM10
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6400': 'AQ_PM10V',

    # Non-volatile PM10
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6401': 'AQ_PM10NV',

    # Volatile PM2.5
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6410': 'AQ_PM25V',

    # Non-volatile PM2.5
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6411': 'AQ_PM25NV',

    # Lead in PM10 (aerosol)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5012': 'AQ_PB',

    # Carbon monoxide
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/38': 'AQ_CO',
    # Nitrogen dioxide (air)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8': 'AQ_NO2',

    # Nitrogen oxides (air) (NOX)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/9': 'AQ_NOX',

    # Sulphur dioxide (air)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1': 'AQ_SO2',

    # Ozone (air)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7': 'AQ_O3',

    # Particulate matter < 2.5 µm (aerosol)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001': 'AQ_PM25',

    # Benzene (air)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/20': 'AQ_C6H6',

    # Cadmium in PM10 (aerosol)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5014': 'AQ_CD',

    # Nickel in PM10 (aerosol)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5015': 'AQ_NI',

    # Arsenic in PM10 (aerosol)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5018': 'AQ_AS',

    # Benzo(a)pyrene in PM10 (aerosol)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5029': 'AQ_BAP',

    # Dibenzo(ah)anthracene in PM10 (aerosol)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5419': 'AQ_C22H14',

    # Perylene in PM10 (aerosol)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5488': 'AQ_C20H12',

    # 5-Methyl Chrysene in PM10 (aerosol)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5522': 'AQ_C19H14',

    # Benzo(b)naphtho(2,1-d)thiophene in PM10 (aerosol)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5524': 'AQ_C16H10S',

    # Benzo(c)phenanthrene in PM10 (aerosol)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5525': 'AQ_C18H12',

    # Cholanthrene in PM10 (aerosol)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5526': 'AQ_C20H14',

    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5527': 'AQ_C22H14',

    # Dibenzo(al)pyrene in PM10 (aerosol)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5528': 'AQ_C24H14',

    # Benzo(a)anthracene in PM10 (aerosol)
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5610': 'AQ_C18H12',

    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5617': 'AQ_C20H12',
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5623': 'AQ_C22H12',
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5626': 'AQ_C20H12',
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5636': 'AQ_24H14',
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5637': 'AQ_C24H14_9106',
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5639': 'AQ_C24H14_9108',
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5655': 'AQ_C22H12',
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5759': 'AQ_C20H12',
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5364': 'AQ_C22H12',
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5381': 'AQ_C20H12',
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5406': 'AQ_C18H12',
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5415': 'AQ_C24H12',
    'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5417': 'AQ_C18H10',
}

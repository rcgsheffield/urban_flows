"""
Data pipeline configuration
"""

import os.path

# Geographical filter
DEFAULT_LOCATION = (53.38297, -1.4659)
DEFAULT_DISTANCE = 30
DEFAULT_UNIT = 'km'

# Data storage directories
DEFAULT_DATA_DIR = 'data'
DEFAULT_RAW_DIR = os.path.join(DEFAULT_DATA_DIR, '0_raw')
DEFAULT_STAGE_DIR = os.path.join(DEFAULT_DATA_DIR, '1_stage')
DEFAULT_CLEAN_DIR = os.path.join(DEFAULT_DATA_DIR, '2_clean')
DEFAULT_DB_DIR = os.path.join(DEFAULT_DATA_DIR, '3_db')
DEFAULT_ASSETS_DIR = 'assets'

# CSV headers
FIELD_NAMES = [
    'StartTime',
    'EndTime',
    # http://dd.eionet.europa.eu/vocabulary/aq/observationverification
    'Verification',
    # http://dd.eionet.europa.eu/vocabulary/aq/observationvalidity
    'Validity',
    'Value',
    'DataCapture',
    'unit_of_measurement',
    'observed_property',
    'station',
    'sampling_point',
]

# Map European Environment Agency metrics to Urban Observatory metadata codes
# European Commission conversion factors at 20 deg C and 1013 mb
# https://uk-air.defra.gov.uk/assets/documents/reports/cat06/0502160851_Conversion_Factors_Between_ppb_and.pdf
# This is a dictionary with nested keys like this: dict[unit][observed_property]
UNIT_MAP = {
    # Micrograms per cubic metre
    'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ug.m-3': {
        # Particulate matter < 10 µm (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5': dict(
            label='AQ_PM10',
            unit='ug/m3',
            factor=1,
        ),
        #  Volatile PM10
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6400': dict(
            label='AQ_PM10V',
            unit='ug/m3',
            factor=1,
        ),
        # Non-volatile PM10
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6401': dict(
            label='AQ_PM10NV',
            unit='ug/m3',
            factor=1,
        ),
        # Volatile PM2.5
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6410': dict(
            label='AQ_PM25V',
            unit='ug/m3',
            factor=1,
        ),
        # Non-volatile PM2.5
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6411': dict(
            label='AQ_PM25NV',
            unit='ug/m3',
            factor=1,
        ),
        # Lead in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5012': dict(
            label='AQ_PB',
            unit='ug/m3',
            factor=1,
        ),
        # Carbon monoxide
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/38': dict(
            label='AQ_CO',
            unit='ppm',
            factor=1 / 1.1642,
        ),
        # Nitrogen dioxide (air)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8': dict(
            label='AQ_NO2',
            unit='ppb',
            factor=1 / 1.9125,
        ),
        # Nitrogen oxides (air) (NOX)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/9': dict(
            label='AQ_NOX',
            unit='ppb',
            factor=1 / 1.9125,
        ),
        # Sulphur dioxide (air)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1': dict(
            label='AQ_SO2',
            unit='ppb',
            factor=1 / 2.6609,
        ),
        # Ozone (air)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7': dict(
            label='AQ_O3',
            unit='ppb',
            factor=1 / 1.9957,
        ),
        # Particulate matter < 2.5 µm (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001': dict(
            label='AQ_PM25',
            unit='ug/m3',
            factor=1,
        ),
        # Benzene (air)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/20': dict(
            label='AQ_C6H6',
            unit='ug/m3',
            factor=1,
        ),
        # 5-Methyl Chrysene in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5522': dict(
            label='AQ_C19H14',
            unit='ng/m3',
            factor=1E3,
        ),
        # Anthanthrene in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5364': dict(
            label='AQ_C22H12',
            unit='ug/m3',
            factor=1,
        ),
        # Cadmium in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5014': dict(
            label='AQ_CD',
            unit='ng/m3',
            factor=1E3,
        ),
        # Nickel in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5015': dict(
            label='AQ_NI',
            unit='ng/m3',
            factor=1E3,
        ),
        # Arsenic in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5018': dict(
            label='AQ_AS',
            unit='ng/m3',
            factor=1E3,
        ),
    },

    # Nanograms per cubic metre of ambient air
    'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ng.m-3': {
        # Benzo(a)pyrene in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5029': dict(
            label='AQ_BAP',
            unit='ng/m3',
            factor=1,
        ),
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5364': dict(
            label='AQ_C22H12',
            unit='ng/m3',
            factor=1,
        ),
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5381': dict(
            label='AQ_C20H12',
            unit='ng/m3',
            factor=1,
        ),
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5406': dict(
            label='AQ_C18H12',
            unit='ng/m3',
            factor=1,
        ),
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5415': dict(
            label='AQ_C24H12',
            unit='ng/m3',
            factor=1,
        ),
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5417': dict(
            label='AQ_C18H10',
            unit='ng/m3',
            factor=1,
        ),
        # Dibenzo(ah)anthracene in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5419': dict(
            label='AQ_C22H14',
            unit='ng/m3',
            factor=1,
        ),
        # Perylene in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5488': dict(
            label='AQ_C20H12',
            unit='ng/m3',
            factor=1,
        ),
        # 5-Methyl Chrysene in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5522': dict(
            label='AQ_C19H14',
            unit='ng/m3',
            factor=1,
        ),
        # Benzo(b)naphtho(2,1-d)thiophene in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5524': dict(
            label='AQ_C16H10S',
            unit='ng/m3',
            factor=1,
        ),
        # Benzo(c)phenanthrene in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5525': dict(
            label='AQ_C18H12',
            unit='ng/m3',
            factor=1,
        ),
        # Cholanthrene in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5526': dict(
            label='AQ_C20H14',
            unit='ng/m3',
            factor=1,
        ),
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5527': dict(
            label='AQ_C22H14',
            unit='ng/m3',
            factor=1,
        ),
        # Dibenzo(al)pyrene in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5528': dict(
            label='AQ_C24H14',
            unit='ng/m3',
            factor=1,
        ),
        # Benzo(a)anthracene in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5610': dict(
            label='AQ_C18H12',
            unit='ng/m3',
            factor=1,
        ),
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5617': dict(
            label='AQ_C20H12',
            unit='ng/m3',
            factor=1,
        ),
        #
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5623': dict(
            label='AQ_C22H12',
            unit='ng/m3',
            factor=1,
        ),
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5626': dict(
            label='AQ_C20H12',
            unit='ng/m3',
            factor=1,
        ),
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5636': dict(
            label='AQ_24H14',
            unit='ng/m3',
            factor=1,
        ),
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5637': dict(
            label='AQ_C24H14_9106',
            unit='ng/m3',
            factor=1,
        ),
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5639': dict(
            label='AQ_C24H14_9108',
            unit='ng/m3',
            factor=1,
        ),
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5655': dict(
            label='AQ_C22H12',
            unit='ng/m3',
            factor=1,
        ),
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5759': dict(
            label='AQ_C20H12',
            unit='ng/m3',
            factor=1,
            pubchem_id=9152,
        ),
        # Lead in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5012': dict(
            label='AQ_C20H12',
            unit='ug/m3',
            factor=1,
            pubchem_id=1E3,
        ),
        # Cadmium in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5014': dict(
            label='AQ_CD',
            unit='ng/m3',
            factor=1,
        ),
        # Nickel in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5015': dict(
            label='AQ_NI',
            unit='ng/m3',
            factor=1,
        ),
        # Arsenic in PM10 (aerosol)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5018': dict(
            label='AQ_AS',
            unit='ng/m3',
            factor=1,
        ),
        # Benzene (air)
        'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/20': dict(
            label='AQ_C6H6',
            unit='ug/m3',
            factor=1E-3,
        ),
    }
}

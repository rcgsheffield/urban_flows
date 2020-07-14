import pathlib

from collections import OrderedDict

DATE_FORMAT = '%Y-%m-%d'
DEFAULT_CONFIG_FILE = str(pathlib.Path.home().joinpath('oizom.cfg'))
FAMILY = 'EMS_AirSonde'
DESC_URL = 'https://terminal.oizom.com/#/u/devices/info'
DEFAULT_AVERAGING_TIME = 5 * 60  # seconds

# Map data labels to the Urban Flows metric names
# See table in docs/Polludrone SMART Parameters Table.pdf
# TODO check new metric names are correct
METRICS = dict(
    t='timestamp',
    sensor='sensor',
    bs='INST_BATTERY_PERCENT',  # battery level
    g1='AQ_CO2',
    g2='AQ_CO',
    g3='AQ_NO2',
    g4='AQ_NH3',
    g5='AQ_O3',
    g6='AQ_H2S',
    g7='AQ_NO',
    g8='AQ_SO2',
    g9='AQ_O2',
    p1='AQ_PM25',
    p2='AQ_PM10',
    p3='AQ_PM1',
    temp='MET_TEMP',  # Celsius
    hum='MET_RH',  # Humidity (%)
    leq='AQ_NOISE',  # Noise average (dB)
    lmin='AQ_NOISE/MIN',  # Noise minimum (dB)
    lmax='AQ_NOISE/PEAK',  # Noise maximum (dB)
    rain='MET_RAIN',  # TODO rainfall (mm)
    light='MET_LIGHT',  # TODO Visible light (lux)
    flood='MET_WATER',  # TODO Flood level (mm)
    uv='MET_UV',  # TODO ultraviolet index
    wd='MET_WIND_DIRECTION',  # TODO Wind direction (degrees)
    ws='MET_WIND_SPEED',  # TODO wind speed (m/s)
    pr='ET_AP',  # Atmospheric Pressure (hPa)
)

UNITS = dict(
    bs='%',
    g1='ppm',
    g2='mg/m3',
    g3='ug/m3',
    g4='ug/m3',
    g5='ug/m3',
    g6='ug/m3',
    g7='ug/m3',
    g8='ug/m3',
    g9='%',
    p1='ug/m3',
    p2='ug/m3',
    p3='ug/m3',
    temp='C',
    hum='%',
    leq='dB',
    lmin='dB',
    lmax='dB',
    rain='mm',
    light='lx',
    flood='mm',
    uv='',  # units of one
    ws='m/s',
    wd='deg',
    pr='hPA',
)

# This determines the order of the columns in the output data
OUTPUT_COLUMNS = (
    'timestamp',
    'sensor',
    'INST_BATTERY_PERCENT',
    'AQ_CO2',
    'AQ_CO',
    'AQ_NO2',
    'AQ_O3',
    'AQ_NO',
    'AQ_SO2',
    'AQ_PM25',
    'AQ_PM10',
    'MET_TEMP',
    'MET_RH',
    'AQ_NOISE',
    'AQ_NOISE/MIN',
    'AQ_NOISE/PEAK',
    'MET_LIGHT',
    'MET_UV'
)

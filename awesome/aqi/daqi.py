import aqi


class Band:
    """
    Air quality pollutant banding categories
    """
    LOW = 'Low'
    MODERATE = 'Moderate'
    HIGH = 'High'
    VERY_HIGH = 'Very High'


class DailyAirQualityIndex(aqi.AirQualityIndex):
    """
    Daily Air Quality Index

    https://uk-air.defra.gov.uk/air-pollution/daqi
    """

    COLUMN_MAP = {
        'AQ_PM25': 'particles_25',
        'AQ_PM10': 'particles_10',
        'AQ_NO2': 'nitrogen_dioxide',
        'AQ_SO2': 'sulphur_dioxide',
        'AQ_O3': 'ozone',
    }

    BANDS = {
        1: Band.LOW,
        2: Band.LOW,
        3: Band.LOW,
        4: Band.MODERATE,
        5: Band.MODERATE,
        6: Band.MODERATE,
        7: Band.HIGH,
        8: Band.HIGH,
        9: Band.HIGH,
        10: Band.VERY_HIGH,
    }

    # Pollutant banding ranges, map of upper thresholds to band index
    THRESHOLDS = dict(
        nitrogen_dioxide=(67, 134, 200, 267, 334, 400, 467, 534, 600),
        sulphur_dioxide=(88, 177, 266, 354, 443, 532, 710, 887, 1064),
        ozone=(33, 66, 100, 120, 140, 160, 187, 213, 240),
        particles_25=(11, 23, 35, 41, 47, 53, 58, 64, 70),
        particles_10=(16, 33, 50, 58, 66, 75, 83, 91, 100),
    )

    RUNNING_AVERAGE_WINDOWS = dict(
        ozone='8H',  # 8 hours
        nitrogen_dioxide='1H',  # 1 hour
        sulphur_dioxide='15min',  # 15 minutes
        particles_25='24H',  # 24 hours
        particles_10='24H',  # 24 hours
    )

    def __init__(self, nitrogen_dioxide: float = None, sulphur_dioxide: float = None, ozone: float = None,
                 particles_25: float = None, particles_10: float = None):
        """
        The overall air pollution index for a site or region is determined by the highest concentration of five
        pollutants. The index is numbered 1-10 and divided into four bands, low (1) to very high (10).

        :param ozone: Ozone running 8-hourly mean. µg/m^3
        :param nitrogen_dioxide: Nitrogen Dioxide hourly mean concentration. µg/m^3
        :param sulphur_dioxide: Sulphur Dioxide 15-minute mean concentration. µg/m^3
        :param particles_25: PM_2.5 Particles 24 hour running mean. µg/m^3
        :param particles_10: PM_10 Particles 24 hour running mean. µg/m^3
        """
        super().__init__(ozone=ozone, nitrogen_dioxide=nitrogen_dioxide, sulphur_dioxide=sulphur_dioxide,
                         particles_25=particles_25, particles_10=particles_10)

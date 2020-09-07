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

    def __init__(self, nitrogen_dioxide: float, sulphur_dioxide: float, ozone: float, particles_25: float,
                 particles_10: float):
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

import aqi


class Band:
    GOOD = 'Good'
    FAIR = 'Fair'
    MODERATE = 'Moderate'
    POOR = 'Poor'
    VERY_POOR = 'Very Poor'
    EXTREMELY_POOR = 'Extremely Poor'


class EuropeanAirQualityIndex(aqi.AirQualityIndex):
    """
    European Air Quality Index

    https://www.eea.europa.eu/themes/air/air-quality-index
    """
    BANDS = {
        1: Band.GOOD,
        2: Band.FAIR,
        3: Band.MODERATE,
        4: Band.POOR,
        5: Band.VERY_POOR,
        6: Band.EXTREMELY_POOR,
    }

class Band:
    LOW = 'Low'
    MODERATE = 'Moderate'
    HIGH = 'High'
    VERY_HIGH = 'Very High'


class AirQualityIndex:
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
    THRESHOLDS = dict()

    @classmethod
    def round(cls, value: float) -> int:
        """
        Round a number to the nearest integer
        """
        return int(round(value, 0))

    def __init__(self, **kwargs):
        """
        Specify pollutant values
        """
        # Store input pollutants and round measurements
        self.pollutants = {key: self.round(value) for key, value in kwargs.items()}

    def __getattr__(self, item):
        return self.calculate_pollutant_index(item)

    def calculate_pollutant_index(self, pollutant: str) -> int:
        """
        :param pollutant: Name of pollutant
        :return: Banding for that pollutant
        """

        value = self.pollutants[pollutant]
        thresholds = self.THRESHOLDS[pollutant]

        for i, threshold in enumerate(thresholds):
            index = i + 1
            if value <= threshold:
                return index

        return self.max_value

    @property
    def pollutant_indexes(self) -> dict:
        return {pollutant: getattr(self, pollutant) for pollutant in self.pollutants.keys()}

    @property
    def index(self) -> int:
        return max(self.pollutant_indexes.values())

    @property
    def min_value(self) -> int:
        return min(self.BANDS.keys())

    @property
    def max_value(self) -> int:
        return max(self.BANDS.keys())

    def validate(self) -> bool:
        return self.min_value <= self.index <= self.max_value

    @property
    def band(self) -> str:
        return self.BANDS[self.index]

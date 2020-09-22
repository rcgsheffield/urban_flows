import abc


class AirQualityIndex(abc.ABC):
    """
    Air Quality Index
    """
    # Map from Urban flows column names to AQI pollutants
    COLUMN_MAP = dict()
    BANDS = dict()
    THRESHOLDS = dict()

    # Map pollutants to running average time offsets
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
    RUNNING_AVERAGE_WINDOWS = dict()

    def __repr__(self):
        kwargs = ', '.join('{}={}'.format(key, value) for key, value in self.pollutants.items())
        return '{}({})'.format(self.__class__.__name__, kwargs)

    def __init__(self, **kwargs):
        """
        Specify pollutant values
        """
        # Store input pollutants and round measurements. Skip missing values
        self.pollutants = {key: self.round(value) for key, value in kwargs.items() if value is not None}

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
        return {pollutant: self.calculate_pollutant_index(pollutant) for pollutant in self.pollutants.keys()}

    @property
    def index(self) -> int:
        try:
            return max(self.pollutant_indexes.values())
        except ValueError:
            # No values input, so return null
            if not self.pollutant_indexes:
                pass
            else:
                raise

    @classmethod
    def round(cls, value: float) -> int:
        """
        Round a number to the nearest integer
        """
        return int(round(value, 0))

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

"""
Calculate unit conversion factors
"""


def molar_volume(temperature: float = 283, atmospheric_pressure: float = 1013.25) -> float:
    """
    Calculate molar volume

    :param temperature: Kelvin
    :param atmospheric_pressure: hPa
    :return:
    """
    return 22.41 * (temperature / 273.16) * (1013 / atmospheric_pressure)


def ppb_to_ugm3(parts_per_billion: float, molar_mass: float) -> float:
    """
    Convert concentration from parts-per-billion to micrograms per cubic metre

    :param parts_per_billion:
    :param molar_mass: g/mol
    :return:
    """
    return parts_per_billion * molar_mass / molar_volume()

from pvgisprototype.constants import (
    ENERGY_UNIT,
    ENERGY_UNIT_K,
    IRRADIANCE_UNIT,
    IRRADIANCE_UNIT_K,
    POWER_UNIT,
    POWER_UNIT_K,
)


def kilofy_unit(value, unit="W", threshold=1000):
    """Converts the unit of a given value to its kilo-equivalent if the
    absolute value is greater than or equal to 1000.

    Parameters
    ----------
    value : float
        The numerical value to potentially convert.
    unit : str
        The current unit of the value, defaulting to 'W' (Watts).

    Returns
    -------
    tuple :
        The converted value and its unit. If the value is 1000 or more, it
        converts the value and changes the unit to 'kW' (kilowatts).

    Examples
    --------
    >>> kilofy_unit(1500, "W", 1000)
    (1.5, "kW")
    >>> kilofy_unit(500, "W", 1000)
    (500, "W")
    """
    if value is not None:
        if abs(value) >= threshold and unit == IRRADIANCE_UNIT:
            return value / 1000, IRRADIANCE_UNIT_K  # update to kilo
        if abs(value) >= threshold and unit == POWER_UNIT:
            return value / 1000, POWER_UNIT_K  # update to kilo
        if abs(value) >= threshold and unit == ENERGY_UNIT:
            return value / 1000, ENERGY_UNIT_K  # update to kilo
    return value, unit

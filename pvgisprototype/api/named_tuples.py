from typing import Tuple
from typing import NamedTuple
from collections import namedtuple
from enum import Enum


class NamedTupleTypes(Enum):
    HOUR_ANGLE_SUNRISE = namedtuple('hour_angle_sunrise', ['value', 'unit'])
    HOUR_ANGLE = namedtuple('hour_angle', ['value', 'unit'])
    SOLAR_TIME = namedtuple('solar_time', ['value', 'unit'])
    SOLAR_ALTITUDE = namedtuple('solar_altitude', ['value', 'unit'])
    SOLAR_AZIMUTH = namedtuple('solar_azimuth', ['value', 'unit'])
    SOLAR_DECLINATION = namedtuple('declination', ['value', 'unit'])                # TODO: Decide if 'solar_declination' or just 'declination'
    FRACTIONAL_YEAR = namedtuple('fractional_year', ['value', 'unit'])
    EQUATION_OF_TIME = namedtuple('equation_of_time', ['value', 'unit'])
    TIME_OFFSET = namedtuple('time_offset', ['value', 'unit'])
    TRUE_SOLAR_TIME = namedtuple('true_solar_time', ['value', 'unit'])
    SOLAR_HOUR_ANGLE = namedtuple('solar_hour_angle', ['value', 'unit'])
    SOLAR_ZENITH = namedtuple('solar_zenith', ['value', 'unit'])
    SOLAR_POSITION = namedtuple('solar_position', ['value', 'unit'])
    COMPASS_SOLAR_AZIMUTH = namedtuple('compass_solar_azimuth', ['value', 'unit'])


def generate(named_tuple_type:str, value_unit_pair:Tuple[float, str])-> NamedTuple:
    """Generate an instance of a named tuple.

    This function is agnostic to the specific type of named tuple that is generated.
    It can generate an instance of any named tuple type defined in the NamedTupleTypes,
    provided that the named_tuple_type argument matches one of the names in the
    NamedTupleTypes.

    Parameters
    ----------
    named_tuple_type : str
        The name of the named tuple type to generate. Must match one of the names in
        the NamedTupleTypes.
    value_unit_pair : tuple
        A tuple containing two elements:
            - value : float 
                The value to set for the 'value' field of the named tuple.
            - unit : str
                The value to set for the 'unit' field of the named tuple.

    Returns
    -------
    NamedTuple
        An instance of the specified named tuple type, with 'value' and 'unit'
        fields set to the elements of value_unit_pair.

    Raises
    ------
    ValueError
        If named_tuple_type does not match any of the names in the NamedTupleTypes.
    """

    if named_tuple_type in NamedTupleTypes.__members__:
        named_tuple_class = NamedTupleTypes[named_tuple_type].value
        return named_tuple_class(*value_unit_pair)
    else:
        raise ValueError(f"Invalid named tuple type: {named_tuple_type}")
    

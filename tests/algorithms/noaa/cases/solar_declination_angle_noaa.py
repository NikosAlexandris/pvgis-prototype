from pandas import Timestamp
from pandas import DatetimeIndex
from numpy import array as numpy_array
from numpy import radians
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype import SolarDeclination
from pvgisprototype.api.utilities.timestamp import generate_datetime_series
from .cases_solar_declination import cases
from .cases_solar_declination import cases_ids


cases_solar_declination_angle_noaa = cases
cases_solar_declination_angle_noaa_ids = cases_ids


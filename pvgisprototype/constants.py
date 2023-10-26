from math import pi
import numpy as np


PARAMETERS_YAML_FILE = 'parameters.yaml'  # definitions
"""
Name of the YAML file that contains various parameter configurations
for PVIS functions.

This YAML file defines the type, initial values, units, and descriptions for
each parameter. The file is organized into sections, each corresponding to a
different 'group' like: 'Where?', 'When?', 'Atmospheric properties', 'Earth
orbit', etc.

Each parameter is described with the following keys:

    - value: Contains 'type' and 'initial' values.
    - unit: Contains 'type' and 'initial' values.
    - symbol: Symbol used for the parameter.
    - description: Textual description of what the parameter represents.

See Also
--------
- Python's PyYAML library for YAML file parsing:
  https://pypi.org/project/PyYAML/

Examples
--------
- Longitude:
    value:
        type: Optional[float]
        initial:
    unit:
        type: Optional[str]
        initial:
    symbol: Λ
    description: "The angle between a point on the Earth's surface and the meridian plane,
                  ranging from 0° at the Prime Meridian to 180° east or west."
"""

VERBOSE_LEVEL_DEFAULT = 0
ROUNDING_PLACES_DEFAULT = 5
TOLERANCE_DEFAULT = 0.1  # Is this a sane default ?
UNITLESS = 'unitless'
RADIANS = 'radians'
ANGLE_OUTPUT_UNITS_DEFAULT = RADIANS
MINUTES = 'minutes'
TIME_OUTPUT_UNITS_DEFAULT = MINUTES
IN_MEMORY_FLAG_DEFAULT = False
MASK_AND_SCALE_FLAG_DEFAULT = False

TIMESTAMPS_FREQUENCY_DEFAULT = 'h'  # hours

LATITUDE_MINIMUM = -90
LATITUDE_MAXIMUM = 90  # in PVGIS : rowoffset
LONGITUDE_MINIMUM = -180
LONGITUDE_MAXIMUM = 180  # in PVGIS : coloffset
ELEVATION_MINIMUM = 0
ELEVATION_MAXIMUM = 8848
HORIZON_HEIGHT_UNIT = 'meters'  # Is it meters? ------------------------------
SOLAR_DECLINATION_MINIMUM = 0
SOLAR_DECLINATION_MAXIMUM = 90

SURFACE_TILT_MINIMUM = 0
SURFACE_TILT_MAXIMUM = 90
SURFACE_TILT_DEFAULT = 45  # degrees
OPTIMISE_SURFACE_TILT_FLAG_DEFAULT = False
OPTIMISE_SURFACE_GEOMETRY_FLAG_DEFAULT = False
SURFACE_ORIENTATION_MINIMUM = 0
SURFACE_ORIENTATION_MAXIMUM = 360
SURFACE_ORIENTATION_DEFAULT = 180  # Due south, counting from North

SOLAR_CONSTANT_MINIMUM = 1360
SOLAR_CONSTANT = 1360.8  # at mean Earth-Sun distance in W/m^2
SOLAR_CONSTANT_TOLERANCE = 0.5
AU = 1  # Earth-Sun distance in Astronomical Units
STEPHAN_BOLTZMANN_CONSTANT = 5.67e-8  # in W/m^2 K^4
EXTRATERRESTRIAL_IRRADIANCE_MIN = 1315  # 1315.2963089821737 for days_in_a_year = 365.25
EXTRATERRESTRIAL_IRRADIANCE_MAX = 1407  # 1406.3049813983132 for days_in_a_year = 365.25

RANDOM_DAY_FLAG_DEFAULT = False
RANDOM_DAY_SERIES_FLAG_DEFAULT = False
FRACTIONAL_YEAR_MINIMUM = 0
FRACTIONAL_YEAR_MAXIMUM = 2 * pi
DAYS_IN_A_YEAR = 365  # RemoveMe & use a function!
PERIGEE_OFFSET = 0.048869
ECCENTRICITY_CORRECTION_FACTOR = 0.03344  # 0.01672

TERM_N_IN_SHADE = 0.25227
TERM_N_COLUMN_NAME = 'term N'
KB_RATIO_COLUMN_NAME = 'Kb'

LINKE_TURBIDITY_MINIMUM = 0
LINKE_TURBIDITY_MAXIMUM = 8
LINKE_TURBIDITY_DEFAULT = 2  # to get going for now
LINKE_TURBIDITY_TIME_SERIES_DEFAULT = LINKE_TURBIDITY_DEFAULT  # to get going for now
LINKE_TURBIDITY_UNIT = UNITLESS
LINKE_TURBIDITY_COLUMN_NAME = 'Linke'
OPTICAL_AIR_MASS_DEFAULT = 2
OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT = OPTICAL_AIR_MASS_DEFAULT
OPTICAL_AIR_MASS_UNIT = UNITLESS
RAYLEIGH_OPTICAL_THICKNESS_UNIT = UNITLESS
ATMOSPHERIC_REFRACTION_FLAG_DEFAULT = True

REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT = 1.5853349194640094  # radians

MEAN_GROUND_ALBEDO_DEFAULT = 2
TIME_OFFSET_GLOBAL_DEFAULT = 0
HOUR_OFFSET_DEFAULT = 0

NO_SOLAR_INCIDENCE = 0  # Solar incidence when shadow is detected

TEMPERATURE_DEFAULT = 25  # Cell temperature under standard test conditions, degrees Celsius.
TEMPERATURE_COLUMN_NAME = 'Temperature'
WIND_SPEED_DEFAULT = 0
WIND_SPEED_COLUMN_NAME = '🌬 Wind speed'
ALBEDO_DEFAULT = 0.2

SYSTEM_EFFICIENCY_DEFAULT = 0.86
EFFICIENCY_DEFAULT = 0.86
EFFICIENCY_COLUMN_NAME = 'Efficiency'

LONGITUDE = 'Longitude'
LONGITUDE_COLUMN_NAME = 'Longitude'
LATITUDE = 'Latitude'
LATITUDE_COLUMN_NAME = 'Latitude'
TIME_ALGORITHM_NAME = 'Time Algorithm'
DECLINATION_NAME = 'Declination'
HOUR_ANGLE_NAME = 'Hour Angle'
POSITION_ALGORITHM_NAME = 'Position Algorithm'
ZENITH_NAME = 'Zenith'
ALTITUDE_NAME = 'Altitude'
AZIMUTH_NAME = 'Azimuth'
INCIDENCE_NAME = 'Incidence'
SOLAR_TIME_NAME = 'Solar Time'
UNITS_NAME = 'Units'
UNITLESSS_NAME = 'Unitless'

# ⊾ ∢ ⦠ ∡ ⦛ ⦜ ⦣ ⦤ ⦥
# ⦨ ⦩ # from horizontal upwards
# ⦪ ⦫ # from horizontal downwards
# ⦮ ⦯ # from vertical upwards
# ⦬ ⦭ # from vertical downwards
# ⭍
# ☀ ☼ 🌣 # sun
# 🗤 # rays spreading
# ⌇ # wavy line
# 🌬 # wind
# ⌖ ⯐ # position
# ⭸ ⭹

SURFACE_TILT_COLUMN_NAME = '∡ Tilt'
TIME_ALGORITHM_COLUMN_NAME = 'Timing'  # Algorithm
DECLINATION_COLUMN_NAME = '∢ Declination'
HOUR_ANGLE_COLUMN_NAME = f':clock12: Hour Angle'
POSITION_ALGORITHM_COLUMN_NAME = '⯐ Positioning'  # Algorithm
ZENITH_COLUMN_NAME = '⦭ Zenith'
ALTITUDE_COLUMN_NAME = '⦩ Altitude'
AZIMUTH_COLUMN_NAME = '⦬ Azimuth'
AZIMUTH_DIFFERENCE_COLUMN_NAME = 'Δ⦬ Azimuth'
INCIDENCE_COLUMN_NAME = 'Incidence'
INCIDENCE_ALGORITHM_COLUMN_NAME = 'Incidence algorithm'
SOLAR_TIME_COLUMN_NAME = 'Solar Time'
SURFACE_TILT_COLUMN_NAME = '∡ Tilt'
SURFACE_ORIENTATION_COLUMN_NAME = '↻ Orientation'
LOSS_COLUMN_NAME = 'Loss'
UNITS_COLUMN_NAME = 'Units'
UNITLESSS_COLUMN_NAME = 'Unitless Column'

NOT_AVAILABLE_COLUMN_NAME = 'NA'
NOT_AVAILABLE = 'NA'
OUT_OF_RANGE_INDICES_COLUMN_NAME = 'Out-of-range'

IRRADIANCE_UNITS = 'W/m²'
ALGORITHM_COLUMN_NAME = 'Algorithm'
IRRADIANCE_ALGORITHM_HOFIERKA_2002 = 'Hofierka, 2002'
EFFECTIVE_IRRADIANCE_COLUMN_NAME = '⭍ Effective'
EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME = 'Direct ⭍'
EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME = 'Diffuse ⭍'
EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME = 'Reflected ⭍'
GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME = 'Global ∡'
GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME = 'Global ⤓'
DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME = 'Direct ∡'
DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME = 'Direct ⭸'
DIFFUSE_INCLINED_IRRADIANCE = 'Diffuse'
DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME = 'Diffuse 🗤∡'
DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME = 'Diffuse 🗤_'
DIFFUSE_CLEAR_SKY_IRRADIANCE_COLUMN_NAME = 'Diffuse clear-sky'
REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME = 'Reflected ⭚∡'
#⭚
#⭛
REFLECTED_HORIZONTAL_IRRADIANCE_COLUMN_NAME = 'Reflected ⭚'
EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME = 'Extra-Normal ⌇'
EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME = 'Extra ⤓'

ABOVE_HORIZON_COLUMN_NAME = "Above horizon"
LOW_ANGLE_COLUMN_NAME = "Low angle"
BELOW_HORIZON_COLUMN_NAME = "Below horizon"
SHADE_COLUMN_NAME = 'Shade'

# from PVGIS

ANGULAR_LOSS_COEFFICIENT = 0.155
EARTHRADIUS = 6371000.  # Earth radius in meters
UNDEFINED = 0.
UNDEFINED_Z = -9999.  # Out of range value?

angular_loss_denominator = 0.155

SCALING_FACTOR = 150
inverse_scale_constant = 1 / SCALING_FACTOR

UNDEF = float('nan')
double_numpi = 2 * np.pi
half_numpi = 0.5 * np.pi

pi_half = pi / 2  # Half of π
pi2 = pi * 2  # 2π
deg2rad = pi / 180  # Conversion factor from degrees to radians
rad2deg = 180 / pi  # Conversion factor from radians to degrees

PERFORMANCE_RATIO = 0.68
FIRSTYEAR = 2007
LASTYEAR = 2014
DUST_TRANSMITTANCE = 1.00
TEMPERATURE_INTERVAL = 1
T_COEFF = 0.035
THRESHOLD = 0.0001
INVERTER_EFF = 0.97
HOUR_ANGLE = pi / 12.0
UNDEF = 0.0  # undefined value for terrain aspect
UNDEFZ = -9999.0  # undefined value for NULL
SKIP = "1"
BIG = 1e20
EPS = 1e-4
STEP = "0.5"
MAX_YEARS = 20
START_VOLTAGE = 14.5
# TILE_SIZE = 2.5
# FIRST_EAST_TILE = 73
DEFAULT_CONSUMPTION_FILE = "hourlyconsumption.txt"
DEFAULT_COEFFICIENTS_FILE = "csi.coeffs"
DEFAULT_POWER_MATRIX_FILE = "matrix_voltages.csv"
DEFAULT_CHARGE_MATRIX_FILE = "battery_voltage.csv"
RADIATION_CUTOFF = 30.0

daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MAX_CURRENTS = 20
MAX_STATES = 20
chargeMatrix = [0.0] * (MAX_CURRENTS * MAX_STATES)

systemEfficiency_global = 1.0

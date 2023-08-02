"""
Constants
"""

from math import pi
import numpy as np

AOI_CONSTANTS = [ -0.074, 0.155]
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

# varCount_global = 0  # Global variable for varCount
# bitCount_global = 0  # Global variable for bitCount
# arrayNumInt = 0  # Global variable for arrayNumInt

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
ALBEDO = 0.2
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

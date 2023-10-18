from devtools import debug
from scipy.integrate import quad
from scipy.optimize import newton
import math
import numpy as np


DAYS_IN_YEAR = 365
EARTH_TILT = math.radians(23.5)  # Earth's tilt in radians
initial_guess = 0.5

# some solar irradiance fnuction
def irradiance(tilt, day):
    declination_angle = EARTH_TILT * math.cos((2 * math.pi / DAYS_IN_YEAR) * (day - 173))
    return -math.cos(tilt - declination_angle) + 1

# the derivative of the solar irradiance function
def derivative(tilt, day):
    declination_angle = EARTH_TILT * math.cos((2 * math.pi / DAYS_IN_YEAR) * (day - 173))
    return math.sin(tilt - declination_angle)

# use scipy's newton function to find the optimal tilt angle
optimal_tilts = []
for day in range(DAYS_IN_YEAR):
    optimal_tilt = newton(derivative, initial_guess, args=(day,))
    optimal_tilts.append(optimal_tilt)

# Print results
for day, tilt in enumerate(optimal_tilts):
    print(f"The optimal tilt angle that maximizes solar irradiance on day {day+1} is: {tilt} radians")

average_optimal_tilt = np.mean(optimal_tilts)
print(f"The average optimal tilt angle that maximizes solar irradiance over the year is: {average_optimal_tilt} radians")

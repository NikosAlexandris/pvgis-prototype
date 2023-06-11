import math
from typing import Union

# from: rsun_base.cpp
# function: com_sol_const(int no_of_day)
def calculate_solar_constant(number_of_day: Union[int, float]) -> float:
    """Compute solar constant.

    The solar constant is the amount of solar electromagnetic radiation
    received at the outer atmosphere of Earth in a unit area perpendicular to
    the rays of the Sun, on a day when Earth is at its mean distance from the
    Sun. Its approximate value is around 1361 W/m^2 but varies slightly
    throughout the year due to the Earth's elliptical orbit.

    Parameters
    ----------
    number_of_day : int, float
        Number of the day in the year counted from 1 (January 1) to 365 or 366
        (December 31).

    Returns
    -------
    float
        Solar constant.

    Notes
    -----
    The `position` of the Earth in its orbit around the Sun is calculated by
    multiplying the number of the day by 2*pi (the full circumference of a
    circle in radians), and then dividing by 365.25 (the average number of days
    in a year, accounting for leap years). The resulting value is an angle in
    radians that represents where in its orbit the Earth is.

    The solar_constant is calculated by taking a base value of 1367 W/m^2 and
    then adjusting it based on the Earth's `position` in its orbit. The
    `adjustment_factor`, 0.03344 * cos(d1 - 0.048869), accounts for the slight
    elliptical shape of the Earth's orbit - the solar constant is a bit higher
    when the Earth is closer to the Sun (perihelion) and a bit lower when it's
    farther away (aphelion).

    Notes from GRASS-GIS' `r.sunlib.c`:

    /* com_sol_const(): compute the Solar Constant corrected for the day of the
       year. The Earth is closest to the Sun (Perigee) on about January 3rd,
       it is furthest from the sun (Apogee) about July 6th. The 1367 W/m^2 solar
       constant is at the average 1AU distance, but on Jan 3 it gets up to
       around 1412.71 W/m^2 and on July 6 it gets down to around 1321 W/m^2.
       This value is for what hits the top of the atmosphere before any energy
       is attenuated. */


    /* Solar constant: 1367.0 W/m^2. Note: solar constant is parameter.

       Perigee offset: here we call Jan 2 at 8:18pm the Perigee, so day
       number 2.8408. In angular units that's (2*pi * 2.8408 / 365.25) =
       0.048869.

       Orbital eccentricity: For Earth this is currently about 0.01672,
       and so the distance to the sun varies by +/- 0.01672 from the
       mean distance (1AU), so over the year the amplitude of the
       function is 2*ecc = 0.03344.

       And 365.25 is of course the number of days in a year.
     */
    """
    position_of_earth = 2 * math.pi * number_of_day / 365.25
    adjustment_factor =  0.03344 * math.cos(position_of_earth - 0.048869)
    solar_constant = 1367 * (1 + adjustment_factor)

    return solar_constant

import math


# from: rsun_base.cpp
# function: com_declin(no_of_day)
def calculate_solar_declination(number_of_day: int) -> float:
    """Approximate the sun's declination for a given day of the year.

    The solar declination is the angle between the Sun's rays and the
    equatorial plane of Earth. The formula uses the `asin` and `sin`
    trigonometric functions to achieve this. 

    Parameters
    ----------
    number_of_day (int): The day of the year (ranging from 1 to 365 or 366 in a leap year).

    Returns
    -------
    float: The solar declination for the given day of the year.

    Notes
    -----

    - The function calculates the `proportion` of the way through the year (in
      radians), which is given by `(2 * pi * number_of_day) / 365.25`.

    - The `0.3978`, `1.4`, and `0.0355` are constants in the approximation
      formula, wi the `0.0489` being an adjustment factor for the slight
      eccentricity of Earth's orbit.
  
    - Finally, the declination is negated (`declination = - declination`). This
      might be due to the coordinate system in use, where a negative
      declination means the sun is in the Southern Hemisphere. This would
      depend on the broader context of the program.

    - Please note that the formula used here is a simple approximation, and
      might not provide highly precise results. For more accurate calculations
      of solar position, comprehensive models like the Solar Position Algorithm
      (SPA) are typically used.
    """
    declination = 2 * math.pi * number_of_day / 365.25
    declination = math.asin(0.3978 * math.sin(declination - 1.4 + 0.0355 * math.sin(declination - 0.0489)))
    declination = - declination

    return declination


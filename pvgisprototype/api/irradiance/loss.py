from devtools import debug
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from typing import List
import math
from math import exp
from math import pi
from math import sin
from math import cos
from math import pow
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import ANGULAR_LOSS_COEFFICIENT
import numpy as np
from rich import print


@log_function_call
def calculate_angular_loss_factor_for_direct_irradiance(
    solar_incidence: float,
    angular_loss_coefficient: float = ANGULAR_LOSS_COEFFICIENT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """Calculate the angular loss factor for the direct horizontal radiation
    based on the solar incidence angle

    The adjustment factor represents the fraction of the original
    `direct_radiation` that is retained after accounting for the loss of
    radiation due to the angle of incidence or the orientation of the surface
    with respect to the sun.

    Parameters
    ----------

    solar_incidence_angle: float
        solar incidence angle
    angular_loss_coefficient: float

    Returns
    -------
    angular_loss_factor: float

    Notes
    -----

    The adjustment involves:

    1. computes the fraction of radiation that is _not_ lost due to
    the `solar_incidence_angle` angle divided by the `solar_declination` ranging between
    0 (complete loss) and 1 (no loss):

        `( 1 - exp( -solar_incidence_angle / angle_of_incidence_constant ) )`

        - The exponential function `exp`, raises the mathematical constant `e`
          (approximately 2.71828) to the power of the given argument.

        - The negative exponential term of the fraction `solar_altitude /
          solar_declination` calculates the exponential decay or attenuation
          factor based on the ratio of `solar_altitude` to the `solar_declination`. 
    
    2. rescales the adjusted value to bring it within a suitable range,
    by multiplying it by the reciprocal of the exponential term with the
    reciprocal of the `solar_declination`:

        `1 / ( 1 - exp( - 1 / solar_declination) )`

    ensuring no excessive amplification or diminishing the effect
    (over-amplification or under-amplification).

    The paper :

        -                            -
        |  1 - exp( -cos(a) / a_r )  |
    1 - | -------------------------- |
        |     1 - exp( -1 / a_r)     |
        -                            -

    In PVGIS :

        ``` c
        angular_loss_denom = 1. / (1 - exp(-1. / a_r));
        br *= (1 - exp(-sh / a_r)) * angular_loss_denom;
        ```

        where:

        - br : direct inclined irradiance
        - sh : _sine_ of _complementary_ solar incidence angle (as per Jenco)
        - a_r : angular loss coefficient


    In pvlib :

        ``` python
        with np.errstate(invalid='ignore'):
            iam = (1 - np.exp(-cosd(aoi) / a_r)) / (1 - np.exp(-1 / a_r))
            iam = np.where(np.abs(aoi) >= 90.0, 0.0, iam)
        ```

        where:

        - iam : incidence angle modifier
        - aoi : angle of incidence
        - a_r : angular loss coefficient
    """
    try:
        numerator = 1 - exp(-cos(solar_incidence) / angular_loss_coefficient)
        # --------------------------------------------------------------------
        denominator =  1 / ( 1 - exp( -1 / angular_loss_coefficient))
        incidence_angle_modifier = numerator / denominator
        if verbose > 0:
            print(f'Incidence angle modifier : {incidence_angle_modifier}')
        return incidence_angle_modifier

    except ZeroDivisionError as e:
        logger.error(f"Zero Division Error: {e}")
        print("Error: Division by zero in calculating the angular loss factor.")
        return 1


@log_function_call
def calculate_angular_loss_factor_for_direct_irradiance_series(
    solar_incidence_series: List[float],
    angular_loss_coefficient: float = ANGULAR_LOSS_COEFFICIENT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
    """
    Notes
    -----
    This function implements the solar incidence angle modifier as per Martin &
    Ruiz (2005). Expected is the angle between the sun-solar-surface vector and
    the vector normal to the reference solar surface. We call this the
    _typical_ incidence angle as opposed to the _complementary_ incidence angle
    defined by Jenco (1992).

    """
    try:
        numerator = 1 - np.exp( - np.cos(solar_incidence_series) / angular_loss_coefficient )
        denominator =  1 / ( 1 - exp( -1 / angular_loss_coefficient))
        incidence_angle_modifier_series = numerator / denominator

        if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
            debug(locals())

        if verbose > 0:
            print(f'Incidence angle modifier series: {incidence_angle_modifier_series}')

        log_data_fingerprint(
            data=incidence_angle_modifier_series,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
        )

        return incidence_angle_modifier_series

    except ZeroDivisionError as e:
        logger.error(f"Zero Division Error: {e}")
        print("Error: Division by zero in calculating the angular loss factor.")
        return np.array([1])  # Return an array with a single element as 1


def calculate_angular_loss_factor_for_nondirect_irradiance(
    indirect_angular_loss_coefficient,
    angular_loss_coefficient = ANGULAR_LOSS_COEFFICIENT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """Calculate the effect of reflectivity at small angles of incidence

    In PVGIS :

    - AOIConstants[0]
    - AOIConstants[1]

    c1 = 4./(3.*M_PI);
    diff_coeff_angleloss = sinslope + (M_PI-sunSlopeGeom->slope - sinslope)
                           /
                           (1+cosslope);
    diff_loss_factor =
                       1. - exp(
                                 - (   c1 * diff_coeff_angleloss
                                     + AOIConstants[0]
                                     * diff_coeff_angleloss
                                     * diff_coeff_angleloss
                                   ) /
                                   AOIConstants[1]);
    """
    angular_loss_coefficient_product = angular_loss_coefficient / 2 - 0.154
    c1 = 4 / (3 * pi)
    loss_factor = 1 - exp(
        -(
            c1 * indirect_angular_loss_coefficient
            + angular_loss_coefficient_product * pow(angular_loss_coefficient, 2)
        )
        / angular_loss_coefficient
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())
        
    return loss_factor

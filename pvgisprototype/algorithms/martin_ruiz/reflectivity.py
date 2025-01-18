from math import exp, pi, pow

import numpy as np
from devtools import debug
from rich import print

from pvgisprototype import SolarIncidence
from pvgisprototype.constants import (
    ANGULAR_LOSS_COEFFICIENT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
def calculate_reflectivity_factor_for_direct_irradiance_series(
    solar_incidence_series: SolarIncidence,
    angular_loss_coefficient: float = ANGULAR_LOSS_COEFFICIENT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
    """Calculate the angular loss factor for the direct horizontal radiation
    based on the solar incidence angle.

    This function implements the solar incidence angle modifier as per Martin &
    Ruiz (2005). Expected is the angle between the sun-solar-surface vector and
    the vector normal to the reference solar surface. We call this the
    _typical_ incidence angle as opposed to the _complementary_ incidence angle
    defined by Jenčo (1992).

    The adjustment factor represents the fraction of the original
    `direct_radiation` that is retained after accounting for the loss of
    radiation due to the angle of incidence or the orientation of the surface
    with respect to the sun.

    Parameters
    ----------
    solar_incidence_series : float
        Solar incidence angle series

    angular_loss_coefficient : float

    Returns
    -------
    reflectivity_factor_series : float

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
        - sh : _sine_ of _complementary_ solar incidence angle (as per Jenčo, 1992)
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

    Review Me : --------------------------------------------------------------

    This function will return a time series `incidence_angle_modifier_series`
    of floating point numbers. As it may generate NaN elements, further
    processing in a time series context, would required attention for example
    when summing arrays with NaN elements.

    To circumvent eventual "problems" and the need for special handling
    downstream in the code, we replace all NaN elements with 0 just before
    returning the final time series.

    """
    logger.info(
            f"> Executing solar radiation modelling function calculate_reflectivity_factor_for_direct_irradiance_series()",
            alt=f"> Executing [underline]solar radiation modelling[/underline] function calculate_reflectivity_factor_for_direct_irradiance_series()"
            )
    try:
        numerator = 1 - np.exp(
            -np.cos(solar_incidence_series) / angular_loss_coefficient
        )
        denominator = 1 / (1 - exp(-1 / angular_loss_coefficient))
        incidence_angle_modifier_series = numerator / denominator
        incidence_angle_modifier_series = np.where(
            np.abs(solar_incidence_series) >= pi / 2, 0, incidence_angle_modifier_series
        )  # Borrowed from pvlib !

        if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
            debug(locals())

        if verbose > 0:
            print(f"Incidence angle modifier series: {incidence_angle_modifier_series}")

        log_data_fingerprint(
            data=incidence_angle_modifier_series,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
        )

        logger.info(
                f"  < Returning incidence angle modifier series :\n{incidence_angle_modifier_series}",
                alt=f"  [green]<[/green] Returning incidence angle modifier series :\n{incidence_angle_modifier_series}",
                )

        return incidence_angle_modifier_series

    # Review-Me !
    except ZeroDivisionError as e:
        logger.error(f"Zero Division Error: {e}")
        print("Error: Division by zero in calculating the angular loss factor.")
        return np.array([1])  # Return an array with a single element as 1


@log_function_call
def calculate_reflectivity_factor_for_nondirect_irradiance(
    indirect_angular_loss_coefficient,
    angular_loss_coefficient=ANGULAR_LOSS_COEFFICIENT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> float:
    """Calculate the reflectivity factor as for small angles of solar
    incidence.

    Notes
    -----

    Review Me : --------------------------------------------------------------

    This function will return a single `incidence_angle_modifier` (or call it
    loss factor) float number. Further processing in a time series context can
    be done by simply replicating the reflectivity factor for all timestamps.

    Further, this structure will not generate any NaNs across a time series
    which often need special handling, i.e. when summing arrays with NaN
    elements.

    Other implementations

    In PVGIS v5.2 :

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
    logger.info(
            f"> Executing solar radiation modelling function calculate_reflectivity_factor_for_nondirect_irradiance()",
            alt=f"> Executing [underline]solar radiation modelling[/underline] function calculate_reflectivity_factor_for_nondirect_irradiance()"
            )
    angular_loss_coefficient_product = angular_loss_coefficient / 2 - 0.154
    c1 = 4 / (3 * pi)
    incidence_angle_modifier = 1 - exp(
        -(
            c1 * indirect_angular_loss_coefficient
            + angular_loss_coefficient_product * pow(angular_loss_coefficient, 2)
        )
        / angular_loss_coefficient
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    logger.info(
            f"  < Returning incidence angle modifier :\n{incidence_angle_modifier}",
            alt=f"  [green]<[/green] Returning incidence angle modifier :\n{incidence_angle_modifier}",
            )

    return incidence_angle_modifier


@log_function_call
def calculate_reflectivity_effect(
    irradiance,
    reflectivity,
):
    """Calculate absolute reflectivity effect

    The total loss due to the reflectivity effect (which depends on the solar
    incidence angle) as the difference of the irradiance after and before.

    Notes
    -----
    Other ideas :

    - Sum of reflectivity effect as a difference between the irradiance time
      series after and before the reflectivity effect, i.e. :

        return reflectivity_effect = np.nansum(irradiance_series * reflectivity - irradiance_series)  # Total lost energy due to AOI over the period

    - Average reflectivity effect :

        REFLECTIVITY_EFFECT_AVERAGE_COLUMN_NAME: np.nanmean(calculate_reflectivity_effect(inclined_irradiance_series, reflectivity_factor_series)),

    """
    effect = (irradiance * reflectivity) - irradiance
    return np.nan_to_num(effect, nan=0)  # safer output ?


@log_function_call
def calculate_reflectivity_effect_percentage(
    irradiance,
    reflectivity,
):
    """ """
    # --------------------------------------------------- Is this safe ? -
    with np.errstate(divide="ignore", invalid="ignore"):
        percentage = np.where(
            irradiance != 0,
            100 * (1 - ((irradiance * reflectivity) / irradiance)),
            0,
        )
    return percentage

#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
"""
This Python module is part of PVGIS' API. It implements functions to calculate
the direct inclined solar irradiance.

_Direct_ or _beam_ irradiance is one of the main components of solar
irradiance. It comes perpendicular from the Sun and is not scattered before it
irradiates a surface.

During a cloudy day the sunlight will be partially absorbed and scattered by
different air molecules. The latter part is defined as the _diffuse_
irradiance. The remaining part is the _direct_ irradiance.
"""

from zoneinfo import ZoneInfo

from devtools import debug
from numpy import ndarray
from pandas import DatetimeIndex
from xarray import DataArray

from pvgisprototype import (
    DirectInclinedIrradianceFromExternalData,
    LinkeTurbidityFactor,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.algorithms.hofierka.irradiance.direct.clear_sky.inclined import calculate_clear_sky_direct_inclined_irradiance_hofierka
from pvgisprototype.algorithms.hofierka.irradiance.direct.inclined import calculate_direct_inclined_irradiance_hofierka
from pvgisprototype.api.datetime.now import now_utc_datetimezone

# from pvgisprototype.api.irradiance.shade import is_surface_in_shade_series
from pvgisprototype.api.position.altitude import model_solar_altitude_series
# from pvgisprototype.api.position.azimuth import model_solar_azimuth_series
from pvgisprototype.api.position.incidence import model_solar_incidence_series
from pvgisprototype.api.position.models import (
    SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    ShadingModel,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.api.position.shading import model_surface_in_shade_series
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    ECCENTRICITY_PHASE_OFFSET,
    RADIANS,
    # UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.algorithms.martin_ruiz.reflectivity import (
    calculate_reflectivity_effect,
    calculate_reflectivity_effect_percentage,
)


@log_function_call
@custom_cached
def calculate_direct_inclined_irradiance(
    longitude: float,
    latitude: float,
    elevation: float,
    surface_orientation: SurfaceOrientation | None = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt | None = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex = str(now_utc_datetimezone()),
    timezone: ZoneInfo | None = None,
    # convert_longitude_360: bool = False,
    direct_horizontal_irradiance: ndarray | None = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = None,
    adjust_for_atmospheric_refraction: bool = True,
    # refracted_solar_zenith: (
    #     float | None
    # ) = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    apply_reflectivity_factor: bool = True,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    # complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> DirectInclinedIrradianceFromExternalData:
    """Calculate the direct irradiance incident on a tilted surface [W*m-2].

    Calculate the direct irradiance on an inclined surface based on the
    solar radiation model by Hofierka, 2002. [1]_

    Notes
    -----
    Bic = B0c sin δexp (equation 11)

    or

          B   ⋅ sin ⎛δ   ⎞
           hc       ⎝ exp⎠         ⎛ W ⎞
    B   = ────────────────     in  ⎜───⎟
     ic       sin ⎛h ⎞             ⎜ -2⎟
                  ⎝ 0⎠             ⎝m  ⎠

        (equation 12)

    where :

    - δexp is the solar incidence angle measured between the sun and an
      inclined surface defined in equation (16).

    or else :

        Direct Inclined = Direct Horizontal * sin( Solar Incidence ) / sin( Solar Altitude )

    The implementation by Hofierka (2002) uses the solar incidence angle
    between the sun-vector and the plane of the reference surface (as per Jenčo,
    1992). This is very important and relates to the hardcoded value `True` for
    the `complementary_incidence_angle` input parameter of the function. We
    call this angle (definition) the _complementary_ incidence angle.

    For the losses due to reflectivity, the incidence angle modifier by Martin
    & Ruiz (2005) expects the incidence angle between the sun-vector and the
    surface-normal. Hence, the respective call of the function
    `calculate_reflectivity_factor_for_direct_irradiance_series()`,
    expects the complement of the angle defined by Jenčo (1992). We call the
    incidence angle expected by the incidence angle modifier by Martin & Ruiz
    (2005) the _typical_ incidence angle.

    See also the documentation of the function
    `calculate_solar_incidence_series_jenco()`.

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    solar_incidence_series = model_solar_incidence_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_incidence_model=solar_incidence_model,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        complementary_incidence_angle=True,  # = Sun-vector To Surface-plane (Jenčo, 1992) !
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
    )
    solar_altitude_series = model_solar_altitude_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        # unrefracted_solar_zenith=unrefracted_solar_zenith,
        # solar_time_model=solar_time_model,
        # eccentricity_phase_offset=eccentricity_phase_offset,
        # eccentricity_amplitude=eccentricity_amplitude,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
    )
    # solar_azimuth_series = model_solar_azimuth_series(
    #     longitude=longitude,
    #     latitude=latitude,
    #     timestamps=timestamps,
    #     timezone=timezone,
    #     solar_position_model=solar_position_model,
    #     adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
    #     # unrefracted_solar_zenith=unrefracted_solar_zenith,
    #     # solar_time_model=solar_time_model,
    #     # eccentricity_phase_offset=eccentricity_phase_offset,
    #     # eccentricity_amplitude=eccentricity_amplitude,
    #     dtype=dtype,
    #     array_backend=array_backend,
    #     verbose=0,
    #     log=log,
    # )
    surface_in_shade_series = model_surface_in_shade_series(
        horizon_profile=horizon_profile,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_time_model=solar_time_model,
        solar_position_model=solar_position_model,
        shading_model=shading_model,
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        # unrefracted_solar_zenith=unrefracted_solar_zenith,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        validate_output=validate_output,
    )
    
    if isinstance(direct_horizontal_irradiance, ndarray):
        direct_inclined_irradiance_series = (
            calculate_direct_inclined_irradiance_hofierka(
                timestamps=timestamps,
                timezone=timezone,
                direct_horizontal_irradiance=direct_horizontal_irradiance,  # FixMe
                apply_reflectivity_factor=apply_reflectivity_factor,
                solar_incidence_series=solar_incidence_series,
                solar_altitude_series=solar_altitude_series,
                # solar_azimuth_series=solar_azimuth_series,
                surface_in_shade_series=surface_in_shade_series,
                dtype=dtype,
                array_backend=array_backend,
                validate_output=validate_output,
                verbose=verbose,
                log=log,
            )
        )
    else:
        direct_inclined_irradiance_series = (
            calculate_clear_sky_direct_inclined_irradiance_hofierka(
                elevation=elevation,
                surface_orientation=surface_orientation,
                surface_tilt=surface_tilt,
                timestamps=timestamps,
                timezone=timezone,
                direct_horizontal_irradiance=direct_horizontal_irradiance,  # FixMe
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                apply_reflectivity_factor=apply_reflectivity_factor,
                solar_incidence_series=solar_incidence_series,
                solar_altitude_series=solar_altitude_series,
                # solar_azimuth_series=solar_azimuth_series,
                surface_in_shade_series=surface_in_shade_series,
                solar_constant=solar_constant,
                eccentricity_phase_offset=eccentricity_phase_offset,
                eccentricity_amplitude=eccentricity_amplitude,
                dtype=dtype,
                array_backend=array_backend,
                validate_output=validate_output,
                verbose=verbose,
                log=log,
            )
        )

    direct_inclined_irradiance_series.reflected = calculate_reflectivity_effect(
            irradiance=direct_inclined_irradiance_series.value_before_reflectivity,
            reflectivity_factor=direct_inclined_irradiance_series.reflectivity_factor,
            )
    direct_inclined_irradiance_series.reflected_percentage = calculate_reflectivity_effect_percentage(
            irradiance=direct_inclined_irradiance_series.value_before_reflectivity,
            reflectivity=direct_inclined_irradiance_series.reflectivity_factor,
            )

    # Angle output units -- Hide it if you can :-)

    direct_inclined_irradiance_series.angle_output_units = angle_output_units
    direct_inclined_irradiance_series.surface_orientation = (
        convert_float_to_degrees_if_requested(
            surface_orientation,
            angle_output_units,
        )
    )
    direct_inclined_irradiance_series.surface_tilt = (
        convert_float_to_degrees_if_requested(surface_tilt, angle_output_units)
    )
    # direct_inclined_irradiance_series.solar_incidence = getattr(
    #     solar_incidence_series, angle_output_units
    # )
    # direct_inclined_irradiance_series.solar_azimuth = getattr(
    #     solar_azimuth_series, angle_output_units
    # )
    direct_inclined_irradiance_series.solar_altitude = getattr(
        solar_altitude_series, angle_output_units
    )

    # Build the structured output
    direct_inclined_irradiance_series.build_output(verbose, fingerprint)
    
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_inclined_irradiance_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return direct_inclined_irradiance_series

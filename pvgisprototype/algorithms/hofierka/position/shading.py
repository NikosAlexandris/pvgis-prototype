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
from devtools import debug
from numpy import where
from xarray import DataArray
from pvgisprototype import HorizonHeight, LocationShading, SolarAltitude, SolarAzimuth
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    RADIANS,
    UNITLESS,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.validation.functions import (
    CalculateSurfaceInShadePVGISInputModel,
    CalculateHorizonHeightSeriesInputModel,
    validate_with_pydantic,
)


@log_function_call
@custom_cached
@validate_with_pydantic(CalculateHorizonHeightSeriesInputModel)
def calculate_horizon_height_series(
    solar_azimuth_series: SolarAzimuth,
    horizon_profile: DataArray | None = None,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> HorizonHeight:
    """ """
    # Ensure _all_ azimuth values are measured in radians !

    # Tolerance for matching azimuths (set this based on acceptable precision)
    # tolerance = finfo(float).eps  # Machine epsilon for floating point comparison
    # or :
    # tolerance = 0.001  # or a smaller value, depending on your precision needs
    # ?

    # select closest azimuth values using Xarray's `sel` with `method="nearest"`
    # closest_horizon_heights = horizon_profile.sel(azimuth=solar_azimuth_series.radians, method="nearest", tolerance=tolerance)

    # # Identify where the tolerance is exceeded (i.e., where interpolation is needed)
    # azimuth_difference = abs(closest_horizon_heights.azimuth - solar_azimuth_series.radians)
    # needs_interpolation = azimuth_difference > tolerance

    # We need the index of the selected values !

    # # Assign exact or almost exact matches from the horizon profile
    # close_enough = ~needs_interpolation
    # horizon_height_series[close_enough] = horizon_profile.sel(azimuth=solar_azimuth_series.radians[close_enough])

    # # Interpolate values not close enough
    # import numpy
    # if numpy.any(needs_interpolation):
    #     horizon_height_series[needs_interpolation] = horizon_profile.interp(
    #         azimuth=solar_azimuth_series.radians[needs_interpolation]
    #     )
    if isinstance(horizon_profile, DataArray):

        if (horizon_profile == 0).all():
            from pvgisprototype.core.arrays import create_array

            # If all values are zero, assume flat terrain
            array_parameters = {
                "shape": solar_azimuth_series.value.shape,
                "dtype": dtype,
                "init_method": "zeros",
                "backend": array_backend,
            }  # Borrow shape from solar_azimuth_series
            horizon_height_series = create_array(**array_parameters)

        else:
            max_horizon_azimuth = horizon_profile.values.max().item()
            max_solar_azimuth = solar_azimuth_series.value.max().item()

            if max_solar_azimuth > max_horizon_azimuth:
                # Before interpollate, append one more pair of solar azimuth at 360 degrees (or 2*pi) and
                # repeat the 0 degrees solar azimuth value at the 360 degrees solar azimuth
                from pvgisprototype.constants import pi
                import xarray as xr

                new_max_horizon_azimuth = 2 * pi
                last_horizon_height_value = horizon_profile[0].values
                new_point = xr.DataArray(
                    [last_horizon_height_value],
                    dims="azimuth",
                    coords={"azimuth": [new_max_horizon_azimuth]},
                )
                horizon_profile = xr.concat([horizon_profile, new_point], dim="azimuth")

            horizon_height_series = horizon_profile.interp(
                azimuth=solar_azimuth_series.radians,
            ).values  # retrieve the NumPy array of values here !

    else:  # we assume a flat terrain
        from pvgisprototype.core.arrays import create_array

        array_parameters = {
            "shape": solar_azimuth_series.value.shape,
            "dtype": dtype,
            "init_method": "zeros",
            "backend": array_backend,
        }  # Borrow shape from solar_azimuth_series
        horizon_height_series = create_array(**array_parameters)

    return HorizonHeight(value=horizon_height_series, unit=RADIANS)


@log_function_call
@custom_cached
@validate_with_pydantic(CalculateSurfaceInShadePVGISInputModel)
def calculate_surface_in_shade_series_pvgis(
    solar_altitude_series: SolarAltitude,
    solar_azimuth_series: SolarAzimuth,
    horizon_profile: DataArray | None = None,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> LocationShading:
    """Determine a time series for when a location of observation (or else in
    the context of photovoltaic analysis a solar surface) is in shade.

    The function compares time series of solar altitude and horizon height, the
    latter measured at directions corresponding to the solar azimuth series.
    The comparison derives a qualitative series of the sun being visible from
    the location of observation or indeed behind the horizon.

    Parameters
    ----------
    solar_altitude_series_array: numpy array
        Array of solar altitude angles for each timestamp.

    Returns
    -------
    NumPy array: Boolean array indicating whether the surface is in shade at
    each timestamp.

    """
    horizon_height_series = calculate_horizon_height_series(
        solar_azimuth_series=solar_azimuth_series,
        horizon_profile=horizon_profile,
        dtype=dtype,
        array_backend=array_backend,
        validate_output=validate_output,
        verbose=verbose,
        log=log,
    )
    horizon_height_series.build_output(verbose=verbose, fingerprint=None)
    surface_in_shade_series = where(
        solar_altitude_series.value < horizon_height_series.value, True, False
    )
    logger.debug(f"In shade : {surface_in_shade_series}")

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=surface_in_shade_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return LocationShading(
        value=surface_in_shade_series,
        unit=UNITLESS,
        solar_altitude=solar_altitude_series.value,
        solar_azimuth=solar_azimuth_series.value,
        horizon_height=horizon_height_series,
        visible=~surface_in_shade_series,
        shading_algorithm="PVGIS",
        solar_positioning_algorithm=solar_altitude_series.solar_positioning_algorithm,
        solar_timing_algorithm=solar_altitude_series.solar_timing_algorithm,
    )

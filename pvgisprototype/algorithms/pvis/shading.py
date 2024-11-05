from devtools import debug
from numpy import ndarray, where
from xarray import DataArray
from pvgisprototype import HorizonHeight, LocationShading
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    UNITLESS,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call


@log_function_call
@custom_cached
def calculate_horizon_height_series(
    solar_azimuth_series,
    horizon_profile: DataArray | None = None,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
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
        horizon_height_series = horizon_profile.interp(
            azimuth=solar_azimuth_series.radians
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

    return HorizonHeight(value=horizon_height_series, unit="radians")


@log_function_call
@custom_cached
# @validate_with_pydantic(CalculateShadeTimeSeriesInputModel)
def calculate_surface_in_shade_series_pvis(
    solar_altitude_series,
    solar_azimuth_series,
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
    surface_in_shade_series = where(
        solar_altitude_series.value < horizon_height_series.value, True, False
    )
    if validate_output:
        pass

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
        altitude=solar_altitude_series.value,
        azimuth=solar_azimuth_series.value,
        horizon_height=horizon_height_series,
        shading_algorithm="PVGIS",
        position_algorithm=solar_altitude_series.position_algorithm,
        timing_algorithm=solar_altitude_series.timing_algorithm,
    )

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
from math import cos
from zoneinfo import ZoneInfo
from devtools import debug
from numpy import asarray
from pandas import DatetimeIndex, Timestamp

from pvgisprototype import (
    ClearSkyDiffuseGroundReflectedInclinedIrradiance,
    LinkeTurbidityFactor,
)
from pvgisprototype.api.irradiance.diffuse.clear_sky.horizontal import (
    calculate_clear_sky_diffuse_horizontal_irradiance,
)
from pvgisprototype.api.irradiance.direct.horizontal import (
    calculate_clear_sky_direct_horizontal_irradiance_series,
)
from pvgisprototype.api.position.models import SolarPositionModel, SolarTimeModel
from pvgisprototype.constants import (
    ALBEDO_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    ECCENTRICITY_PHASE_OFFSET,
    SOLAR_CONSTANT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.arrays import create_array
from pvgisprototype.validation.values import identify_values_out_of_range


@log_function_call
@custom_cached
def calculate_clear_sky_ground_reflected_inclined_irradiance_series_pvgis(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: DatetimeIndex = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo = ZoneInfo('UTC'),
    surface_orientation: float = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: float = SURFACE_TILT_DEFAULT,
    surface_tilt_threshold = SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    # unrefracted_solar_zenith: UnrefractedSolarZenith | None = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    albedo: float | None = ALBEDO_DEFAULT,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> ClearSkyDiffuseGroundReflectedInclinedIrradiance:
    """Calculate the clear-sky diffuse ground reflected irradiance on an inclined surface (Ri).

    The calculation assumes isotropy. The ground reflected clear-sky irradiance
    received on an inclined surface [W.m-2] is proportional to the global
    horizontal irradiance Ghc, to the mean ground albedo ρg and a fraction of
    the ground viewed by an inclined surface rg(γN).

    Parameters
    ----------
    longitude : float
        longitude
    latitude : float
        latitude
    elevation : float
        elevation
    timestamps : DatetimeIndex
        timestamps
    timezone : ZoneInfo
        timezone
    surface_orientation : float
        surface_orientation
    surface_tilt : float
        surface_tilt
    surface_tilt_threshold :
        surface_tilt_threshold
    linke_turbidity_factor_series : LinkeTurbidityFactor
        linke_turbidity_factor_series
    adjust_for_atmospheric_refraction : bool
        adjust_for_atmospheric_refraction
    albedo : float | None
        albedo
    global_horizontal_irradiance : ndarray | None
        global_horizontal_irradiance
    solar_position_model : SolarPositionModel
        solar_position_model
    solar_time_model : SolarTimeModel
        solar_time_model
    solar_constant : float
        solar_constant
    eccentricity_phase_offset : float
        eccentricity_phase_offset
    eccentricity_amplitude : float
        eccentricity_amplitude
    dtype : str
        dtype
    array_backend : str
        array_backend
    verbose : int
        verbose
    log : int
        log

    """
    # build reusable parameter dictionaries
    coordinates = {
        'longitude': longitude,
        'latitude': latitude,
    }
    time = {
        'timestamps': timestamps,
        'timezone': timezone,
    }
    solar_positioning = {
        'solar_position_model': solar_position_model,
        'adjust_for_atmospheric_refraction': adjust_for_atmospheric_refraction,
        'solar_time_model': solar_time_model,
    }
    earth_orbit = {
        'eccentricity_phase_offset': eccentricity_phase_offset,
        'eccentricity_amplitude': eccentricity_amplitude,
    }
    array_parameters = {
        "dtype": dtype,
        "array_backend": array_backend,
    }
    output_parameters = {
        'verbose': verbose,  # Is this wanted here ? i.e. not setting = 0 ?
        'log': log,
    }

    if surface_tilt <= surface_tilt_threshold:  # No ground reflection for a flat or nearly flat surface
        ground_view_fraction = 0
        # in order to avoid 'NameError's
        flat_surface_array_parameters = {
            "shape": timestamps.shape,
            "dtype": dtype,
            "init_method": "zeros",
            "backend": array_backend,
        }  # Borrow shape from timestamps
        global_horizontal_irradiance_series = create_array(**flat_surface_array_parameters)

    else:
        ground_view_fraction = (1 - cos(surface_tilt)) / 2

    direct_horizontal_irradiance_series = calculate_clear_sky_direct_horizontal_irradiance_series(
        **coordinates,
        elevation=elevation,
        **time,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        solar_time_model=solar_time_model,
        solar_constant=solar_constant,
        **earth_orbit,
        **array_parameters,
        **output_parameters,
    )
    diffuse_horizontal_irradiance_series = calculate_clear_sky_diffuse_horizontal_irradiance(
        **coordinates,
        **time,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        # unrefracted_solar_zenith=unrefracted_solar_zenith,
        **solar_positioning,
        solar_constant=solar_constant,
        **earth_orbit,
        **array_parameters,
        **output_parameters,
    )
    global_horizontal_irradiance_series = (
        direct_horizontal_irradiance_series.value
        + diffuse_horizontal_irradiance_series.value
    )
    # --------------------------------------------------------------------
    # At this point, the `global_horizontal_irradiance_series` is either :
    # _read_ from external time series  Or  simulated 
    # --------------------------------------------------------------------

    ground_reflected_inclined_irradiance_series = asarray(
        global_horizontal_irradiance_series * ground_view_fraction * albedo,
        dtype=dtype
    ).reshape(-1)

    out_of_range, out_of_range_index = identify_values_out_of_range(
        series=ground_reflected_inclined_irradiance_series,
        shape=timestamps.shape,
        data_model=ClearSkyDiffuseGroundReflectedInclinedIrradiance(),
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=ground_reflected_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    # Common output structure
    function_output = {
        "value": ground_reflected_inclined_irradiance_series,
        "out_of_range": out_of_range,
        "out_of_range_index": out_of_range_index,
        "ground_view_fraction": ground_view_fraction,
        "albedo": albedo,
        "global_horizontal_irradiance": global_horizontal_irradiance_series,
        "direct_horizontal_irradiance": (
            direct_horizontal_irradiance_series
            if "direct_horizontal_irradiance_series" in locals()
            else None
        ),
        "diffuse_horizontal_irradiance": (
            diffuse_horizontal_irradiance_series
            if "diffuse_horizontal_irradiance_series" in locals()
            else None
        ),
        "solar_positioning_algorithm": getattr(
            diffuse_horizontal_irradiance_series,
            "solar_positioning_algorithm",
            None,
        ),
        "solar_timing_algorithm": getattr(
            diffuse_horizontal_irradiance_series, "solar_timing_algorithm", None
        ),
        "location": (longitude, latitude),
        "elevation": elevation,
        "surface_orientation": surface_orientation,
        "surface_tilt": surface_tilt,
        "surface_tilt_threshold": surface_tilt_threshold,
    }
    return ClearSkyDiffuseGroundReflectedInclinedIrradiance(**function_output)

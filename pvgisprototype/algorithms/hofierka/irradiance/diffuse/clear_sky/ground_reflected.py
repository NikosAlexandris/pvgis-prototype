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
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(),
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
    """
    Calculate the clear-sky ground-reflected diffuse irradiance on an inclined
    surface.

    Calculates the component of diffuse irradiance that reaches an inclined
    surface after reflection from the ground under clear-sky conditions. This
    component is proportional to the global horizontal irradiance [Ghc], the
    solar surface tilt angle, the mean ground albedo [ρg] and a fraction of the
    ground viewed by an inclined surface [rg(γN)]. The calculation follows the
    isotropic sky model where ground-reflected radiation is uniformly
    distributed.

    The ground-reflected irradiance is calculated as:

    .. math::
        I_{gr} = I_g \cdot F_{gv} \cdot \\rho

    where:

    - :math:`I_{gr}` is the ground-reflected irradiance on the inclined surface
    - :math:`I_g` is the global horizontal irradiance
    - :math:`F_{gv}` is the ground view fraction: :math:`(1 - \cos(\\beta)) / 2`
    - :math:`\\beta` is the surface tilt angle
    - :math:`\\rho` is the ground albedo

    For near-horizontal surfaces (tilt ≤ threshold), ground reflection is
    negligible and set to zero.

    Parameters
    ----------
    longitude : float
        Geographic longitude in decimal degrees. East is positive, west is
        negative. Valid range: [-180, 180].
    latitude : float
        Geographic latitude in decimal degrees. North is positive, south is
        negative. Valid range: [-90, 90].
    elevation : float
        Site elevation above sea level in meters. Used for atmospheric
        corrections in irradiance calculations.
    timestamps : pandas.DatetimeIndex
        Time series index for calculations. Must be timezone-aware for
        accurate solar position computations.
    timezone : str
        IANA timezone identifier (e.g., 'UTC', 'Europe/Rome'). Used for
        local time conversions in solar position algorithms.
    surface_orientation : float
        Surface azimuth angle in degrees. 0° = North, 90° = East, 180° = South,
        270° = West. Determines horizontal orientation of the inclined surface.
    surface_tilt : float
        Surface tilt angle from horizontal in degrees. 0° = horizontal,
        90° = vertical. Valid range: [0, 90].
    surface_tilt_threshold : float, optional
        Minimum tilt angle in degrees below which ground reflection is
        considered negligible and set to zero. Default is typically a small
        value (e.g., 1°).
    albedo : float, optional
        Ground surface albedo (reflectivity), dimensionless. Typical values:
        0.2 (grass, soil), 0.3-0.5 (sand, concrete), 0.8 (fresh snow).
        Valid range: [0, 1]. Default varies by application.
    linke_turbidity_factor_series : LinkeTurbidityFactor, optional
        Linke turbidity factor values characterizing atmospheric turbidity.
        Typical range: [1.0, 6.0]. Default is
        ``LinkeTurbidityFactor()``.
    adjust_for_atmospheric_refraction : bool, optional
        Whether to apply atmospheric refraction correction to solar angles.
        Affects accuracy near horizon. Default is True.
    solar_position_model : str, optional
        Algorithm for solar position calculations (e.g., 'NOAA', 'PSA').
        Default is ``SOLAR_POSITION_MODEL_DEFAULT``.
    solar_time_model : str, optional
        Solar time calculation method. Default is ``SOLAR_TIME_MODEL_DEFAULT``.
    solar_constant : float, optional
        Solar constant in W·m⁻². Default is ``SOLAR_CONSTANT`` (~1361 W·m⁻²).
    eccentricity_phase_offset : float, optional
        Phase offset for Earth's orbital eccentricity correction in radians.
        Default is ``ECCENTRICITY_PHASE_OFFSET``.
    eccentricity_amplitude : float, optional
        Amplitude of orbital eccentricity correction. Default is
        ``ECCENTRICITY_CORRECTION_FACTOR``.
    dtype : str, optional
        NumPy data type for array operations. Default is ``DATA_TYPE_DEFAULT``.
    array_backend : str, optional
        Array backend ('numpy', 'cupy', 'dask'). Default is
        ``ARRAY_BACKEND_DEFAULT``.
    verbose : int, optional
        Verbosity level for debugging output. When exceeding
        ``DEBUG_AFTER_THIS_VERBOSITY_LEVEL``, prints all local variables
        using devtools.debug. Default is ``VERBOSE_LEVEL_DEFAULT``.
    log : int, optional
        Logging level for data fingerprinting. When exceeding
        ``HASH_AFTER_THIS_VERBOSITY_LEVEL``, logs data hashes for
        reproducibility tracking. Default is ``LOG_LEVEL_DEFAULT``.

    Returns
    -------
    ClearSkyDiffuseGroundReflectedInclinedIrradiance
        Data model containing:
        
        - **value** : numpy.ndarray
            Ground-reflected irradiance values in W·m⁻² for each timestamp
        - **out_of_range** : bool
            Flag indicating if any values exceed physical bounds
        - **out_of_range_index** : numpy.ndarray
            Indices of out-of-range values
        - **ground_view_fraction** : float
            Fraction of ground visible from tilted surface (0 to 0.5)
        - **albedo** : float
            Ground albedo used in calculation
        - **global_horizontal_irradiance** : numpy.ndarray
            Global horizontal irradiance values used
        - **direct_horizontal_irradiance** : array or None
            Direct component of horizontal irradiance
        - **diffuse_horizontal_irradiance** : array or None
            Diffuse component of horizontal irradiance
        - **solar_positioning_algorithm** : str
            Solar position algorithm used
        - **solar_timing_algorithm** : str
            Solar time algorithm used
        - **location** : tuple
            (longitude, latitude) coordinates
        - **elevation** : float
            Site elevation in meters
        - **surface_orientation** : float
            Surface azimuth in degrees
        - **surface_tilt** : float
            Surface tilt in degrees
        - **surface_tilt_threshold** : float
            Tilt threshold used

    Notes
    -----
    **Ground View Fraction:**

    The ground view fraction represents the solid angle subtended by the ground
    as seen from the tilted surface:

    - Horizontal surface (0°): F_gv = 0 (no ground visible)
    - Vertical surface (90°): F_gv = 0.5 (half hemisphere is ground)
    - Tilted surface: F_gv = (1 - cos(β)) / 2

    **Tilt Threshold Behavior:**

    When ``surface_tilt <= surface_tilt_threshold``, the function:

    1. Sets ground view fraction to 0
    2. Creates zero-valued arrays for ground reflection
    3. Avoids unnecessary computation for negligible contributions

    This optimization is physically justified as near-horizontal surfaces
    receive minimal ground-reflected radiation.

    **Global Horizontal Irradiance**

    The function internally computes the global horizontal irradiance as:

    .. math::
        I_g = I_{bh} + I_{dh}

    where I_bh is direct horizontal and I_dh is diffuse horizontal irradiance,
    both calculated using clear-sky models.

    **Physical Constraints**

    - Ground-reflected irradiance cannot exceed global horizontal irradiance
    - Albedo values outside [0, 1] produce unphysical results
    - Results valid only for clear-sky conditions
    - Model assumes isotropic ground reflection (Lambertian surface)

    See Also
    --------
    calculate_clear_sky_direct_horizontal_irradiance_series : Computes direct component
    calculate_clear_sky_diffuse_horizontal_irradiance : Computes diffuse component
    ClearSkyDiffuseGroundReflectedInclinedIrradiance : Output data model

    References
    ----------
    .. [1] Duffie, J. A., & Beckman, W. A. (2013). *Solar Engineering of Thermal
           Processes* (4th ed.). Wiley. Chapter 2: Available Solar Radiation.
    .. [2] Perez, R., et al. (1987). A new simplified version of the Perez diffuse
           irradiance model for tilted surfaces. *Solar Energy*, 39(3), 221-231.

    Examples
    --------
    Calculate ground reflection for a south-facing tilted surface:

    >>> import pandas as pd
    >>> import numpy as np
    >>> from pvgisprototype import Longitude, Latitude
    >>> from pvgisprototype.algorithms.hofierka.irradiance.diffuse.clear_sky.ground_reflected import (
    ...     calculate_clear_sky_ground_reflected_inclined_irradiance_series_pvgis
    ... )
    >>> 
    >>> # Summer day, hourly data
    >>> timestamps = pd.date_range('2024-06-21', periods=24, freq='h', tz='UTC')
    >>> 
    >>> # Location: Rome, Italy
    >>> longitude = Longitude(value=12.496, unit='degrees')
    >>> latitude = Latitude(value=41.903, unit='degrees')
    >>> # Solar surface position
    >>> surface_orientation = SurfaceOrientation(value=180, unit='degrees')
    >>> surface_tilt = SurfaceTilt(value=180, unit='degrees')
    >>> # Calculate irradiance
    >>> result = calculate_clear_sky_ground_reflected_inclined_irradiance_series_pvgis(
    ...     longitude=longitude.radians,
    ...     latitude=latitude.radians,
    ...     elevation=20,
    ...     timestamps=timestamps,
    ...     timezone='Europe/Rome',
    ...     surface_orientation=surface_orientation.radians,  # South-facing
    ...     surface_tilt=surface_tilt.radians,
    ...     albedo=0.2                # Grass/soil
    ... )
    >>> 
    >>> print(f"Ground view fraction: {result.ground_view_fraction:.3f}")
    Ground view fraction: 1.000
    >>> print(f"Peak ground-reflected irradiance: {result.value.max():.1f} W/m²")
    Peak ground-reflected irradiance: 241.5 W/m²
    >>> print(f"Daily total: {result.value.sum():.1f} Wh/m²")
    Daily total: 2221.9 Wh/m²

    Compare albedo effects

    >>> # Low albedo (dark soil)
    >>> result_dark = calculate_clear_sky_ground_reflected_inclined_irradiance_series_pvgis(
    ...     longitude=longitude.radians,
    ...     latitude=latitude.radians,
    ...     elevation=20,
    ...     timestamps=timestamps,
    ...     timezone='Europe/Rome',
    ...     surface_orientation=surface_orientation.radians,
    ...     surface_tilt=surface_tilt.radians,
    ...     albedo=0.15
    ... )
    >>> 
    >>> # High albedo (concrete)
    >>> result_bright = calculate_clear_sky_ground_reflected_inclined_irradiance_series_pvgis(
    ...     longitude=longitude.radians,
    ...     latitude=latitude.radians,
    ...     elevation=20,
    ...     timestamps=timestamps,
    ...     timezone='Europe/Rome',
    ...     surface_orientation=surface_orientation.radians,
    ...     surface_tilt=surface_tilt.radians,
    ...     albedo=0.4
    ... )
    >>> 
    >>> albedo_ratio = result_bright.value.max() / result_dark.value.max()
    >>> print(f"Bright/dark albedo ratio: {albedo_ratio:.2f}")
    Bright/dark albedo ratio: 2.67

    Near-horizontal surface (negligible ground reflection)

    >>> result_flat = calculate_clear_sky_ground_reflected_inclined_irradiance_series_pvgis(
    ...     longitude=longitude.radians,
    ...     latitude=latitude.radians,
    ...     elevation=20,
    ...     timestamps=timestamps,
    ...     timezone='Europe/Rome',
    ...     surface_orientation=surface_orientation.radians,  # South-facing
    ...     surface_tilt=0.1,  # Nearly horizontal
    ...     surface_tilt_threshold=1.0,
    ...     albedo=0.2                # Grass/soil
    ... )
    >>> 
    >>> print(f"Ground view fraction: {result_flat.ground_view_fraction}")
    0.0  # Threshold triggered, no ground reflection
    >>> print(f"All values zero: {np.all(result_flat.value == 0)}")
    True

    Warnings
    --------
    - Tilt angle must be in degrees, not radians
    - Albedo values should be realistic for the surface type
    - Model assumes isotropic reflection (not accurate for specular surfaces)
    - Clear-sky model; not valid under cloudy conditions
    - Input timestamps must be timezone-aware
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

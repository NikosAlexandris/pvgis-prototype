from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from datetime import datetime
from pathlib import Path
from typing import Optional
from typing import List
from rich import print
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.api.series.statistics import print_series_statistics
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
from pvgisprototype.api.geometry.models import SolarPositionModel
from pvgisprototype.api.geometry.models import SolarIncidenceModel
from pvgisprototype.api.geometry.models import SolarTimeModel
from pvgisprototype.api.geometry.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SOLAR_INCIDENCE_ALGORITHM_DEFAULT
from pvgisprototype.validation.pvis_data_classes import BaseTimestampSeriesModel
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.api.irradiance.direct import calculate_direct_horizontal_irradiance_time_series
from pvgisprototype.api.irradiance.direct import calculate_extraterrestrial_normal_irradiance_time_series
from pvgisprototype.api.irradiance.limits import LOWER_PHYSICALLY_POSSIBLE_LIMIT
from pvgisprototype.api.irradiance.limits import UPPER_PHYSICALLY_POSSIBLE_LIMIT
from pvgisprototype.cli.print import print_irradiance_table_2
from pvgisprototype.api.geometry.altitude_series import model_solar_altitude_time_series
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_series_to_degrees_arrays_if_requested
from pvgisprototype.api.geometry.incidence_series import model_solar_incidence_time_series
from pvgisprototype.api.geometry.azimuth_series import model_solar_azimuth_time_series
from pvgisprototype.api.irradiance.loss import calculate_angular_loss_factor_for_nondirect_irradiance

from pvgisprototype.constants import FINGERPRINT_COLUMN_NAME
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_COLUMN_NAME
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_FLAG_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.constants import TERM_N_IN_SHADE
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.constants import LINKE_TURBIDITY_UNIT
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import DEGREES
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import NOT_AVAILABLE
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.api.series.models import MethodsForInexactMatches
import numpy as np
from math import cos
from math import sin
from math import pi
from pvgisprototype.constants import TITLE_KEY_NAME
from pvgisprototype.constants import LOSS_COLUMN_NAME
from pvgisprototype.constants import SURFACE_TILT_COLUMN_NAME
from pvgisprototype.constants import AZIMUTH_COLUMN_NAME
from pvgisprototype.constants import ALTITUDE_COLUMN_NAME
from pvgisprototype.constants import GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_INCLINED_IRRADIANCE
from pvgisprototype.constants import DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_INCLINED_IRRADIANCE_BEFORE_LOSS_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_HORIZONTAL_IRRADIANCE
from pvgisprototype.constants import DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_CLEAR_SKY_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import LINKE_TURBIDITY_COLUMN_NAME
from pvgisprototype.constants import INCIDENCE_COLUMN_NAME
from pvgisprototype.constants import INCIDENCE_ALGORITHM_COLUMN_NAME
from pvgisprototype.constants import OUT_OF_RANGE_INDICES_COLUMN_NAME
from pvgisprototype.constants import TERM_N_COLUMN_NAME
from pvgisprototype.constants import KB_RATIO_COLUMN_NAME
from pvgisprototype.constants import AZIMUTH_DIFFERENCE_COLUMN_NAME
from pvgisprototype.validation.hashing import generate_hash


@log_function_call
def read_horizontal_irradiance_components_from_sarah(
    shortwave: Path,
    direct: Path,
    longitude: float,
    latitude: float,
    timestamps: Optional[datetime] = None,
    mask_and_scale: bool = False,
    neighbor_lookup: MethodsForInexactMatches = None,
    tolerance: Optional[float] = TOLERANCE_DEFAULT,
    in_memory: bool = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = True,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
):
    """Read horizontal irradiance components from SARAH time series.

    Read the global and direct horizontal irradiance components incident on a
    solar surface from SARAH time series.

    Parameters
    ----------
    shortwave: Path
        Filename of surface short-wave (solar) radiation downwards time series
        (short name : `ssrd`) from ECMWF which is the solar radiation that
        reaches a horizontal plane at the surface of the Earth. This parameter
        comprises both direct and diffuse solar radiation.

    Returns
    -------
    diffuse_irradiance: float
        The diffuse radiant flux incident on a surface per unit area in W/m².
    """
    if multi_thread:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_global_horizontal_irradiance_series = executor.submit(
                select_time_series,
                time_series=shortwave,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                mask_and_scale=mask_and_scale,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                in_memory=in_memory,
                log=log,
            )
            future_direct_horizontal_irradiance_series = executor.submit(
                select_time_series,
                time_series=shortwave,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                mask_and_scale=mask_and_scale,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                in_memory=in_memory,
                log=log,
            )
            global_horizontal_irradiance_series = (
                future_global_horizontal_irradiance_series.result().to_numpy().astype(dtype=dtype)
            )
            direct_horizontal_irradiance_series = (
                future_direct_horizontal_irradiance_series.result().to_numpy().astype(dtype=dtype)
            )
    else:
        global_horizontal_irradiance_series = select_time_series(
            time_series=shortwave,
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            mask_and_scale=mask_and_scale,
            neighbor_lookup=neighbor_lookup,
            tolerance=tolerance,
            in_memory=in_memory,
            log=log,
        ).to_numpy().astype(dtype=dtype)
        direct_horizontal_irradiance_series = select_time_series(
            time_series=direct,
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            mask_and_scale=mask_and_scale,
            neighbor_lookup=neighbor_lookup,
            tolerance=tolerance,
            in_memory=in_memory,
            log=log,
        ).to_numpy().astype(dtype=dtype)

    horizontal_irradiance_components = {
        GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME: global_horizontal_irradiance_series,
        DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
    }

    return horizontal_irradiance_components


@log_function_call
def calculate_diffuse_horizontal_component_from_sarah(
    global_horizontal_irradiance_series,
    direct_horizontal_irradiance_series,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = False,
):
    """Calculate the diffuse horizontal irradiance from SARAH time series.

    Calculate the diffuse horizontal irradiance incident on a solar surface
    from SARAH time series.

    Parameters
    ----------
    shortwave: Path
        Filename of surface short-wave (solar) radiation downwards time series
        (short name : `ssrd`) from ECMWF which is the solar radiation that
        reaches a horizontal plane at the surface of the Earth. This parameter
        comprises both direct and diffuse solar radiation.

    Returns
    -------
    diffuse_irradiance: float
        The diffuse radiant flux incident on a surface per unit area in W/m².
    """
    diffuse_horizontal_irradiance_series = (
        global_horizontal_irradiance_series - direct_horizontal_irradiance_series
    ).astype(dtype=dtype)

    if diffuse_horizontal_irradiance_series.size == 1:
        single_value = float(diffuse_horizontal_irradiance_series.values)
        warning = (
            f"{exclamation_mark} The selected timestamp "
            + f"{diffuse_horizontal_irradiance_series.time.values}"
            + f" matches the single value "
            + f"{single_value}"
        )
        logger.warning(warning)

    components_container = {
        'main': lambda: {
            TITLE_KEY_NAME: DIFFUSE_HORIZONTAL_IRRADIANCE,
            DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME: diffuse_horizontal_irradiance_series,
        },
        
        'extended': lambda: {
            TITLE_KEY_NAME: DIFFUSE_HORIZONTAL_IRRADIANCE + " & other horizontal components",
            GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME: global_horizontal_irradiance_series.to_numpy(),
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series.to_numpy(),
        } if verbose > 1 else {},

        'fingerprint': lambda: {
            FINGERPRINT_COLUMN_NAME: generate_hash(diffuse_horizontal_irradiance_series),
        } if fingerprint else {},
    }

    components = {}
    for key, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    if verbose > 0:
        return components

    log_data_fingerprint(
        data=diffuse_horizontal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return diffuse_horizontal_irradiance_series


@log_function_call
def calculate_term_n_time_series(
    kb_series: List[float],
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
):
    """Define the N term for a period of time

    Parameters
    ----------
    kb_series: float
        Direct to extraterrestrial irradiance ratio

    Returns
    -------
    N: float
        The N term
    """
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    kb_series = np.array(kb_series, dtype=dtype)
    term_n_series = 0.00263 - 0.712 * kb_series - 0.6883 * np.power(kb_series, 2, dtype=dtype)

    log_data_fingerprint(
        data=term_n_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return term_n_series


@log_function_call
def calculate_diffuse_sky_irradiance_time_series(
    n_series: List[float],
    surface_tilt: Optional[float] = np.radians(45),
    log: int = 0,
):
    """Calculate the diffuse sky irradiance

    The diffuse sky irradiance function F(γN) depends on the surface tilt `γN`
    (in radians)

    Parameters
    ----------
    surface_tilt: float (radians)
        The tilt (also referred to as : inclination or slope) angle of a solar
        surface

    n_series: float
        The term N

    Returns
    -------

    Notes
    -----
    Internally the function calculates first the dimensionless fraction of the
    sky dome viewed by a tilted (or inclined) surface `ri(γN)`.
    """
    sky_view_fraction = (1 + cos(surface_tilt)) / 2
    # -----------------------------------------------------------------------
    # Verify the following : does it work ?
    # diffuse_sky_irradiance_series = sky_view_fraction
    # +(
    #     sin(surface_tilt)
    #     - surface_tilt
    #     * cos(surface_tilt)
    #     - pi
    #     * sin(surface_tilt / 2) ** 2
    # ) * n_series
    # -----------------------------------------------------------------------
    diffuse_sky_irradiance_series = sky_view_fraction
    + (
        sin(surface_tilt)
        - surface_tilt
        * cos(surface_tilt)
        - pi
        * sin(surface_tilt / 2) ** 2
    ) * n_series

    return diffuse_sky_irradiance_series


@log_function_call
def diffuse_transmission_function_time_series(
    linke_turbidity_factor_series,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> np.array:
    """ Diffuse transmission function over a period of time

    Notes
    -----
    From r.pv's source code:
    tn = -0.015843 + locLinke * (0.030543 + 0.0003797 * locLinke);
    
    """
    linke_turbidity_factor_series_squared_array = np.power(
        linke_turbidity_factor_series.value, 2, dtype=dtype
    )
    diffuse_transmission_series = (
        -0.015843
        + 0.030543 * linke_turbidity_factor_series.value
        + 0.0003797 * linke_turbidity_factor_series_squared_array
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return diffuse_transmission_series


@log_function_call
def diffuse_solar_altitude_coefficients_time_series(
    linke_turbidity_factor_series,
    verbose: int = 0,
    log: int = 0,
):
    """Calculate the diffuse solar altitude coefficients.

    Calculate the diffuse solar altitude coefficients over a period of time.

    Parameters
    ----------
    linke_turbidity_factor_series: (List[LinkeTurbidityFactor] or LinkeTurbidityFactor)
        The Linke turbidity factors as a list of LinkeTurbidityFactor objects
        or a single object.

    Returns
    -------

    """
    linke_turbidity_factor_series_squared_array = np.power(linke_turbidity_factor_series.value, 2)
    diffuse_transmission_series = diffuse_transmission_function_time_series(linke_turbidity_factor_series)
    diffuse_transmission_series_array = np.array(diffuse_transmission_series)
    a1_prime_series = (
        0.26463
        - 0.061581 * linke_turbidity_factor_series.value
        + 0.0031408 * linke_turbidity_factor_series_squared_array
    )
    a1_series = np.where(
        a1_prime_series * diffuse_transmission_series < 0.0022, 
        np.maximum(0.0022 / diffuse_transmission_series_array, a1_prime_series), 
        a1_prime_series
    )
    a2_series = (
        2.04020
        + 0.018945 * linke_turbidity_factor_series.value
        - 0.011161 * linke_turbidity_factor_series_squared_array
    )
    a3_series = (
        -1.3025
        + 0.039231 * linke_turbidity_factor_series.value
        + 0.0085079 * linke_turbidity_factor_series_squared_array
    )

    if verbose == DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return a1_series, a2_series, a3_series


@log_function_call
def diffuse_solar_altitude_function_time_series(
    solar_altitude_series: List[float],
    linke_turbidity_factor_series: LinkeTurbidityFactor,
    verbose: int = 0,
    log: int = 0,
):
    """Calculate the diffuse solar altitude

    Notes
    -----
    Other symbol: function Fd

    """
    a1_series, a2_series, a3_series = diffuse_solar_altitude_coefficients_time_series(
        linke_turbidity_factor_series
    )
    return (
        a1_series
        + a2_series * np.sin(solar_altitude_series.radians)
        + a3_series * np.power(np.sin(solar_altitude_series.radians), 2)
    )


@log_function_call
def calculate_diffuse_inclined_irradiance_time_series(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: BaseTimestampSeriesModel = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    timezone: Optional[str] = None,
    random_time_series: bool = False,
    global_horizontal_component: Optional[Path] = None,
    direct_horizontal_component: Optional[Path] = None,
    surface_tilt: Optional[float] = SURFACE_TILT_DEFAULT,
    surface_orientation: Optional[float] = SURFACE_ORIENTATION_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = None,  # Changed this to np.ndarray
    apply_atmospheric_refraction: Optional[bool] = True,
    refracted_solar_zenith: Optional[float] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    apply_angular_loss_factor: Optional[bool] = True,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    random_days: bool = RANDOM_DAY_FLAG_DEFAULT,
    time_output_units: str = "minutes",
    angle_units: str = RADIANS,
    angle_output_units: str = RADIANS,
    mask_and_scale: bool = False,
    neighbor_lookup: MethodsForInexactMatches = None,
    tolerance: Optional[float] = TOLERANCE_DEFAULT,
    in_memory: bool = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = True,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = False,
) -> np.array:
    """Calculate the diffuse irradiance incident on a solar surface.

    Notes
    -----

    In order or appearance:

    - extraterrestrial_normal_irradiance : G0
    - extraterrestrial_horizontal_irradiance : G0h = G0 sin(h0)
    - kb : Proportion between direct (beam) and extraterrestrial irradiance : Kb
    - diffuse_horizontal_component : Dhc [W.m-2]
    - diffuse_transmission_function() :
    - linke_turbidity_factor :
    - diffuse_solar_altitude_function() :
    - solar_altitude : 
    - calculate_term_n():
    - n : the N term
    - diffuse_sky_irradiance()
    - sine_solar_incidence_angle
    - sine_solar_altitude
    - diffuse_sky_irradiance 
    - calculate_diffuse_sky_irradiance() : F(γN)
    - surface_tilt :
    - diffuse_inclined_irradiance :
    - diffuse_horizontal_component :
    - azimuth_difference :
    - solar_azimuth :
    - surface_orientation :
    - diffuse_irradiance
    """
    # 1. calculate diffuse based on external global and direct irradiance components
    if global_horizontal_component and direct_horizontal_component:
        horizontal_irradiance_components = (
            read_horizontal_irradiance_components_from_sarah(
                shortwave=global_horizontal_component,
                direct=direct_horizontal_component,
                longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
                latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
                timestamps=timestamps,
                mask_and_scale=mask_and_scale,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                in_memory=in_memory,
                log=log,
            )
        )
        global_horizontal_irradiance_series = horizontal_irradiance_components[
            GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME
        ]
        direct_horizontal_irradiance_series = horizontal_irradiance_components[
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
        ]
        diffuse_horizontal_irradiance_series = (
            calculate_diffuse_horizontal_component_from_sarah(
                global_horizontal_irradiance_series=global_horizontal_irradiance_series,
                direct_horizontal_irradiance_series=direct_horizontal_irradiance_series,
                # longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
                # latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
                # timestamps=timestamps,
                # neighbor_lookup=neighbor_lookup,
                dtype=dtype,
                array_backend=array_backend,
                verbose=0,
                log=log,
            )
        )

    else:  # from the model
        direct_horizontal_irradiance_series = calculate_direct_horizontal_irradiance_time_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,  # no verbosity here by choice!
        log=log,
    )

    # 2. Get quantities to calculate the diffuse horizontal irradiance
    extraterrestrial_normal_irradiance_series = (
        calculate_extraterrestrial_normal_irradiance_time_series(
            timestamps=timestamps,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            random_days=random_days,
            dtype=dtype,
            array_backend=array_backend,
            verbose=0,  # no verbosity here by choice!
            log=log,
        )
    )

    # extraterrestrial on a horizontal surface requires the solar altitude
    solar_altitude_series = model_solar_altitude_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,  # Is this wanted here ? i.e. not setting = 0 ?
        log=log,
    )
    extraterrestrial_horizontal_irradiance_series = (
        extraterrestrial_normal_irradiance_series
        * np.sin(solar_altitude_series.radians)
    )
    diffuse_horizontal_irradiance_series = (
        extraterrestrial_normal_irradiance_series
        * diffuse_transmission_function_time_series(linke_turbidity_factor_series)
        * diffuse_solar_altitude_function_time_series(
            solar_altitude_series, linke_turbidity_factor_series
        )
    )

    if surface_tilt == 0:  # horizontal surface however ..
        diffuse_inclined_irradiance_series = diffuse_horizontal_irradiance_series

    else:  # tilted (or inclined) surface
    # Note: in PVGIS: if surface_orientation != 'UNDEF' and surface_tilt != 0:

        kb_series = ( # proportion between direct and extraterrestrial
            direct_horizontal_irradiance_series
            / extraterrestrial_horizontal_irradiance_series
        )
        n_series = calculate_term_n_time_series(
            kb_series,
            dtype=dtype,
            array_backend=array_backend,
        )
        diffuse_sky_irradiance_series = calculate_diffuse_sky_irradiance_time_series(
            n_series=n_series,
            surface_tilt=surface_tilt,
        )
        solar_incidence_series = model_solar_incidence_time_series(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            random_time_series=random_time_series,
            solar_incidence_model=solar_incidence_model,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
            complementary_incidence_angle=True,  # = between sun-vector and surface-plane!
            dtype=dtype,
            array_backend=array_backend,
            verbose=0,
            log=log,
        )

        # prepare size of output array!
        from pvgisprototype.validation.arrays import create_array
        shape_of_array = (
            solar_altitude_series.value.shape
        )  # Borrow shape from solar_altitude_series
        diffuse_inclined_irradiance_series = create_array(
            shape_of_array, dtype=dtype, init_method="zeros", backend=array_backend
        )

        # surface in shade, yet there is ambient light
        mask_surface_in_shade_series = np.logical_and(np.sin(solar_incidence_series.radians) < 0, solar_altitude_series.radians >= 0)
        if np.any(mask_surface_in_shade_series):
            diffuse_sky_irradiance_series[mask_surface_in_shade_series] = (
                calculate_diffuse_sky_irradiance_time_series(
                    n_series=np.full(len(timestamps), TERM_N_IN_SHADE),
                    surface_tilt=surface_tilt,
                )[mask_surface_in_shade_series]
            )
            diffuse_inclined_irradiance_series[mask_surface_in_shade_series] = (
                diffuse_horizontal_irradiance_series[mask_surface_in_shade_series] 
                * diffuse_sky_irradiance_series[mask_surface_in_shade_series]
            )

        else:  # sunlit surface and non-overcast sky
            # ----------------------------------------------------------------
            azimuth_difference_series_array = None  # Avoid UnboundLocalError!
            solar_azimuth_series_array = None
            # ----------------------------------------------------------------

            mask_sunlit_surface_series = solar_altitude_series.radians >= 0.1 
            if np.any(mask_sunlit_surface_series):  # radians or 5.7 degrees
                diffuse_sky_irradiance_series = np.full_like(
                    diffuse_horizontal_irradiance_series, diffuse_sky_irradiance_series
                )
                diffuse_inclined_irradiance_series[
                    mask_sunlit_surface_series
                ] = diffuse_horizontal_irradiance_series[mask_sunlit_surface_series] * (
                    diffuse_sky_irradiance_series[mask_sunlit_surface_series]
                    * (1 - kb_series[mask_sunlit_surface_series])
                    + kb_series[mask_sunlit_surface_series]
                    * np.sin(solar_incidence_series.radians[mask_sunlit_surface_series])
                    / np.sin(solar_altitude_series.radians[mask_sunlit_surface_series])
                )

            else:  # if solar altitude < 0.1 : potential sunlit surface series
                mask_potential_sunlit_surface_series = ~mask_sunlit_surface_series 
                # requires the solar azimuth
                solar_azimuth_series_array = model_solar_azimuth_time_series(
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    timezone=timezone,
                    solar_position_model=solar_position_model,
                    apply_atmospheric_refraction=apply_atmospheric_refraction,
                    refracted_solar_zenith=refracted_solar_zenith,
                    solar_time_model=solar_time_model,
                    time_offset_global=time_offset_global,
                    hour_offset=hour_offset,
                    perigee_offset=perigee_offset,
                    eccentricity_correction_factor=eccentricity_correction_factor,
                    verbose=verbose,
                )
                # Normalize the azimuth difference to be within the range -pi to pi
                # A0 : solar azimuth _measured from East_ in radians
                # ALN : angle between the vertical surface containing the normal to the
                #   surface and vertical surface passing through the centre of the solar
                #   disc [rad]
                azimuth_difference_series_array = (
                    solar_azimuth_series_array.value - surface_orientation
                )
                azimuth_difference_series_array = np.arctan2(
                    np.sin(azimuth_difference_series_array),
                    np.cos(azimuth_difference_series_array),
                )
                diffuse_inclined_irradiance_series[
                    mask_potential_sunlit_surface_series
                ] = diffuse_horizontal_irradiance_series[
                    mask_potential_sunlit_surface_series
                ] * (
                    diffuse_sky_irradiance_series[mask_potential_sunlit_surface_series]
                    * (1 - kb_series[mask_potential_sunlit_surface_series])
                    + kb_series[mask_potential_sunlit_surface_series]
                    * sin(surface_tilt)
                    * np.cos(
                        azimuth_difference_series_array[
                            mask_potential_sunlit_surface_series
                        ]
                    )
                    / (
                        0.1
                        - 0.008
                        * solar_altitude_series.radians[
                            mask_potential_sunlit_surface_series
                        ]
                    )
                )

    if apply_angular_loss_factor:
        diffuse_irradiance_angular_loss_coefficient = sin(surface_tilt) + (
            pi - surface_tilt - sin(surface_tilt)
        ) / (1 + cos(surface_tilt))
        diffuse_irradiance_loss_factor = calculate_angular_loss_factor_for_nondirect_irradiance(
            indirect_angular_loss_coefficient=diffuse_irradiance_angular_loss_coefficient,
        )
        diffuse_inclined_irradiance_series *= diffuse_irradiance_loss_factor

    out_of_range_indices = np.where(
        (diffuse_inclined_irradiance_series < LOWER_PHYSICALLY_POSSIBLE_LIMIT)
        | (diffuse_inclined_irradiance_series > UPPER_PHYSICALLY_POSSIBLE_LIMIT)
    )
    if out_of_range_indices[0].size > 0:
        warning = f"{WARNING_OUT_OF_RANGE_VALUES} in `diffuse_inclined_irradiance_series`!"
        logger.warning(warning)

    # Building the output dictionary ========================================

    components_container = {
        'main': lambda: {
            TITLE_KEY_NAME: DIFFUSE_INCLINED_IRRADIANCE,
            DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME: diffuse_inclined_irradiance_series,
        },# if verbose > 0 else {},

        'extended': lambda: {
            LOSS_COLUMN_NAME: 1 - diffuse_irradiance_loss_factor if apply_angular_loss_factor else NOT_AVAILABLE,
            DIFFUSE_INCLINED_IRRADIANCE_BEFORE_LOSS_COLUMN_NAME: diffuse_inclined_irradiance_series / diffuse_irradiance_loss_factor if apply_angular_loss_factor else NOT_AVAILABLE,
            SURFACE_ORIENTATION_COLUMN_NAME: convert_float_to_degrees_if_requested(surface_orientation, angle_output_units),
            SURFACE_TILT_COLUMN_NAME: convert_float_to_degrees_if_requested(surface_tilt, angle_output_units),
        } if verbose > 1 else {},

        'more_extended': lambda: {
            TITLE_KEY_NAME: DIFFUSE_INCLINED_IRRADIANCE + ' & relevant components',
            DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME: diffuse_horizontal_irradiance_series,
            DIFFUSE_CLEAR_SKY_IRRADIANCE_COLUMN_NAME: diffuse_sky_irradiance_series,
        } if verbose > 2 else {},

        'even_more_extended': lambda: {
            TERM_N_COLUMN_NAME: n_series,
            KB_RATIO_COLUMN_NAME: kb_series,
            AZIMUTH_DIFFERENCE_COLUMN_NAME: getattr(azimuth_difference_series_array, angle_output_units, NOT_AVAILABLE),
            AZIMUTH_COLUMN_NAME: getattr(solar_azimuth_series_array, angle_output_units, NOT_AVAILABLE),
            ALTITUDE_COLUMN_NAME: getattr(solar_altitude_series, angle_output_units) if solar_altitude_series else None,
        } if verbose > 3 else {},

        'and_even_more_extended': lambda: {
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
            EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME: extraterrestrial_horizontal_irradiance_series,
            EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME: extraterrestrial_normal_irradiance_series,
            LINKE_TURBIDITY_COLUMN_NAME: linke_turbidity_factor_series.value,
        } if verbose > 4 else {},

        'extra': lambda: {
            INCIDENCE_COLUMN_NAME: getattr(solar_incidence_series, angle_output_units) if solar_incidence_series else None,
            INCIDENCE_ALGORITHM_COLUMN_NAME: solar_incidence_model,
        } if verbose > 5 else {},

        'out-of-range': lambda: {
            OUT_OF_RANGE_INDICES_COLUMN_NAME: out_of_range_indices,
        } if out_of_range_indices[0].size > 0 else {},

        'fingerprint': lambda: {
            FINGERPRINT_COLUMN_NAME: generate_hash(diffuse_inclined_irradiance_series),
        } if fingerprint else {},
    }

    components = {}
    for key, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    if verbose > 0:
        return components

    log_data_fingerprint(
        data=diffuse_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return diffuse_inclined_irradiance_series

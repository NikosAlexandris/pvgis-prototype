from math import cos, pi, sin
from pathlib import Path

import numpy as np
from devtools import debug
from numpy import diff, where
from pandas import DatetimeIndex

from pvgisprototype import (
    Irradiance,
    LinkeTurbidityFactor,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.api.irradiance.diffuse.altitude import (
    calculate_diffuse_sky_irradiance_series,
    calculate_diffuse_solar_altitude_function_series,
    calculate_term_n_series,
    diffuse_transmission_function_series,
)
from pvgisprototype.api.irradiance.diffuse.horizontal_from_sarah import (
    calculate_diffuse_horizontal_component_from_sarah,
    read_horizontal_irradiance_components_from_sarah,
)
from pvgisprototype.api.irradiance.direct.horizontal import (
    calculate_direct_horizontal_irradiance_series,
)
from pvgisprototype.api.irradiance.extraterrestrial import (
    calculate_extraterrestrial_normal_irradiance_series,
)
from pvgisprototype.api.irradiance.limits import (
    LOWER_PHYSICALLY_POSSIBLE_LIMIT,
    UPPER_PHYSICALLY_POSSIBLE_LIMIT,
)
from pvgisprototype.api.irradiance.reflectivity import (
    calculate_reflectivity_effect,
    calculate_reflectivity_effect_percentage,
    calculate_reflectivity_factor_for_nondirect_irradiance,
)
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.azimuth import model_solar_azimuth_series
from pvgisprototype.api.position.incidence import model_solar_incidence_series
from pvgisprototype.api.position.models import (
    SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ALTITUDE_COLUMN_NAME,
    ANGLE_UNITS_COLUMN_NAME,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    AZIMUTH_COLUMN_NAME,
    AZIMUTH_DIFFERENCE_COLUMN_NAME,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DEGREES,
    DIFFUSE_CLEAR_SKY_IRRADIANCE_COLUMN_NAME,
    DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    DIFFUSE_INCLINED_IRRADIANCE,
    DIFFUSE_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME,
    DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR,
    ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME,
    EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IN_MEMORY_FLAG_DEFAULT,
    INCIDENCE_ALGORITHM_COLUMN_NAME,
    INCIDENCE_COLUMN_NAME,
    IRRADIANCE_UNIT,
    KB_RATIO_COLUMN_NAME,
    LINKE_TURBIDITY_COLUMN_NAME,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    MULTI_THREAD_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    NOT_AVAILABLE,
    OUT_OF_RANGE_INDICES_COLUMN_NAME,
    PERIGEE_OFFSET,
    PERIGEE_OFFSET_COLUMN_NAME,
    POSITION_ALGORITHM_COLUMN_NAME,
    RADIANS,
    RADIATION_MODEL_COLUMN_NAME,
    REFLECTIVITY_COLUMN_NAME,
    REFLECTIVITY_FACTOR_COLUMN_NAME,
    REFLECTIVITY_PERCENTAGE_COLUMN_NAME,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    SOLAR_CONSTANT_COLUMN_NAME,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_COLUMN_NAME,
    SURFACE_TILT_DEFAULT,
    TERM_N_COLUMN_NAME,
    TERM_N_IN_SHADE,
    TIME_ALGORITHM_COLUMN_NAME,
    TITLE_KEY_NAME,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.core.arrays import create_array
from pvgisprototype.core.hashing import generate_hash


@log_function_call
def calculate_diffuse_inclined_irradiance_series(
    longitude: float,
    latitude: float,
    elevation: float,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex = None,
    timezone: str | None = None,
    global_horizontal_component: Path | None = None,
    direct_horizontal_component: Path | None = None,
    mask_and_scale: bool = MASK_AND_SCALE_FLAG_DEFAULT,
    neighbor_lookup: MethodForInexactMatches = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: float | None = TOLERANCE_DEFAULT,
    in_memory: bool = IN_MEMORY_FLAG_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    apply_reflectivity_factor: bool = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    # complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,  # Let Me Hardcoded, Read the docstring!
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = MULTI_THREAD_FLAG_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> Irradiance:
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
    # Some quantities are not always required, hence set them to avoid UnboundLocalError!
    solar_azimuth_series_array = NOT_AVAILABLE
    azimuth_difference_series_array = NOT_AVAILABLE

    # Calculate quantities required : ---------------------------- >>> >>> >>>
    # 1. to model the diffuse horizontal irradiance [optional]
    # 2. to calculate the diffuse sky ... to consider shaded, sunlit and potentially sunlit surfaces
    #
    extraterrestrial_normal_irradiance_series = (
        calculate_extraterrestrial_normal_irradiance_series(
            timestamps=timestamps,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
            verbose=0,  # no verbosity here by choice!
            log=log,
        )
    )
    # extraterrestrial on a horizontal surface requires the solar altitude
    solar_altitude_series = model_solar_altitude_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,  # Is this wanted here ? i.e. not setting = 0 ?
        log=log,
    )
    extraterrestrial_horizontal_irradiance_series = (
        extraterrestrial_normal_irradiance_series.value
        * np.sin(solar_altitude_series.radians)
    )
    extraterrestrial_horizontal_irradiance_series[solar_altitude_series.radians < 0] = (
        0  # In the context of PVGIS, does it make sense to have negative extraterrestrial horizontal irradiance
    )
    # Calculate quantities required : ---------------------------- <<< <<< <<<

    # ----------------------------------- Diffuse Horizontal Irradiance -- >>>
    # Based on external global and direct irradiance components
    if global_horizontal_component and direct_horizontal_component:
        if verbose > 0:
            logger.info(
                ":information: Reading the global and direct horizontal irradiance components from external data ...",
                alt=f":information: [black on white][bold]Reading[/bold] the [orange]global[/orange] and [yellow]direct[/yellow] horizontal irradiance components [bold]from external data[/bold] ...[/black on white]"
            )
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
                multi_thread=multi_thread,
                verbose=verbose,
                log=log,
            )
        )
        global_horizontal_irradiance_series = horizontal_irradiance_components[
            GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME
        ]
        direct_horizontal_irradiance_series = horizontal_irradiance_components[
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
        ]
        diffuse_horizontal_irradiance_series = calculate_diffuse_horizontal_component_from_sarah(
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
        ).value  # Important !

    else:  # OR from the model
        if verbose > 0:
            logger.info(
                ":information: Modelling clear-sky diffuse horizontal irradiance ...",
                alt=":information: [bold]Modelling[/bold] clear-sky diffuse horizontal irradiance ..."
            )
        # global_horizontal_irradiance_series = NOT_AVAILABLE
        global_horizontal_irradiance_series = create_array(
            timestamps.shape, dtype=dtype, init_method=np.nan, backend=array_backend
        )

        # in which case, however: we need the direct component for the kb series, if it's NOT read fom external series!
        direct_horizontal_irradiance_series = (
            calculate_direct_horizontal_irradiance_series(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                timestamps=timestamps,
                timezone=timezone,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                solar_time_model=solar_time_model,
                solar_constant=solar_constant,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                angle_output_units=angle_output_units,
                dtype=dtype,
                array_backend=array_backend,
                verbose=0,  # no verbosity here by choice!
                log=log,
            )
        ).value  # Important !
        diffuse_horizontal_irradiance_series = (
            extraterrestrial_normal_irradiance_series.value
            * diffuse_transmission_function_series(linke_turbidity_factor_series)
            * calculate_diffuse_solar_altitude_function_series(
                solar_altitude_series, linke_turbidity_factor_series
            )
        )
    # ----------------------------------- Diffuse Horizontal Irradiance -- <<<

    # At this point, the diffuse_horizontal_irradiance_series are either :
    # calculated from external time series  Or  modelled

    # if surface_tilt == 0:  # horizontally flat surface
    surface_tilt_threshold = 0.0001
    if surface_tilt <= surface_tilt_threshold:
        diffuse_inclined_irradiance_series = np.copy(
            diffuse_horizontal_irradiance_series
        )
        # to not break the output !
        diffuse_sky_irradiance_series = NOT_AVAILABLE
        n_series = NOT_AVAILABLE
        kb_series = NOT_AVAILABLE
        # azimuth_difference_series_array = NOT_AVAILABLE
        solar_incidence_series = NOT_AVAILABLE

    else:  # tilted (or inclined) surface
        # Note: in PVGIS: if surface_orientation != 'UNDEF' and surface_tilt != 0:
        # --------------------------------------------------- Is this safe ? -
        with np.errstate(divide="ignore", invalid="ignore"):
            kb_series = (  # proportion between direct and extraterrestrial
                direct_horizontal_irradiance_series
                / extraterrestrial_horizontal_irradiance_series
            )
        n_series = calculate_term_n_series(
            kb_series,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
        )
        diffuse_sky_irradiance_series = where(
            np.isnan(n_series),  # handle NaN cases
            0,
            calculate_diffuse_sky_irradiance_series(
                n_series=n_series,
                surface_tilt=surface_tilt,
            ),
        )

        solar_incidence_series = model_solar_incidence_series(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            solar_incidence_model=solar_incidence_model,
            complementary_incidence_angle=True,  # True = between sun-vector and surface-plane !
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

        # prepare size of output array!
        diffuse_inclined_irradiance_series = create_array(
            timestamps.shape, dtype=dtype, init_method="zeros", backend=array_backend
        )

        # prepare cases : surfaces in shade, sunlit, potentially sunlit

        #  --------------------------------------------------------- Review Me
        mask_surface_in_shade_series = np.logical_and(
            np.sin(solar_incidence_series.radians) < 0,
            solar_altitude_series.radians >= 0,
        )  # in shade, yet there is ambient light
        # Should this be the _complementary_ incidence angle series ?
        #  Review Me ---------------------------------------------------------

        mask_sunlit_surface_series = solar_altitude_series.radians >= 0.1  # or >= 5.7 degrees
        mask_potentially_sunlit_surface_series = ~mask_sunlit_surface_series

        if np.any(mask_surface_in_shade_series):
            diffuse_sky_irradiance_series[mask_surface_in_shade_series] = (
                calculate_diffuse_sky_irradiance_series(
                    n_series=np.full(len(timestamps), TERM_N_IN_SHADE),
                    surface_tilt=surface_tilt,
                )[mask_surface_in_shade_series]
            )
            diffuse_inclined_irradiance_series[mask_surface_in_shade_series] = (
                diffuse_horizontal_irradiance_series[mask_surface_in_shade_series]
                * diffuse_sky_irradiance_series[mask_surface_in_shade_series]
            )

        # else:  # sunlit surface and non-overcast sky
        #     # ----------------------------------------------------------------
        #     solar_azimuth_series_array = None
        #     # ----------------------------------------------------------------
        if np.any(mask_sunlit_surface_series):
            diffuse_inclined_irradiance_series[
                mask_sunlit_surface_series
            ] = diffuse_horizontal_irradiance_series[mask_sunlit_surface_series] * (
                diffuse_sky_irradiance_series[mask_sunlit_surface_series]
                * (1 - kb_series[mask_sunlit_surface_series])
                + kb_series[mask_sunlit_surface_series]
                * np.sin(
                    solar_incidence_series.radians[mask_sunlit_surface_series]
                )  # Should be the _complementary_ incidence angle!
                / np.sin(solar_altitude_series.radians[mask_sunlit_surface_series])
            )

        # else:  # if solar altitude < 0.1 : potentially sunlit surface series
        if np.any(mask_potentially_sunlit_surface_series):
            # requires the solar azimuth
            solar_azimuth_series_array = model_solar_azimuth_series(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                timezone=timezone,
                solar_position_model=solar_position_model,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                solar_time_model=solar_time_model,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                verbose=verbose,
            )
            # Normalize the azimuth difference to be within the range -pi to pi
            # A0 : solar azimuth _measured from East_ in radians
            # ALN : angle between the vertical surface containing the normal to the
            #   surface and vertical surface passing through the centre of the solar
            #   disc [rad]
            if isinstance(surface_orientation, SurfaceOrientation): # FIXME This should always be SurfaceOrientation instance and MUST BE FIXED with pydantic!
                surface_orientation = surface_orientation.value
            
            azimuth_difference_series_array = (
                    solar_azimuth_series_array.value - surface_orientation
                )
            azimuth_difference_series_array = np.arctan2(
                np.sin(azimuth_difference_series_array),
                np.cos(azimuth_difference_series_array),
            )
            diffuse_inclined_irradiance_series[
                mask_potentially_sunlit_surface_series
            ] = diffuse_horizontal_irradiance_series[
                mask_potentially_sunlit_surface_series
            ] * (
                diffuse_sky_irradiance_series[mask_potentially_sunlit_surface_series]
                * (1 - kb_series[mask_potentially_sunlit_surface_series])
                + kb_series[mask_potentially_sunlit_surface_series]
                * sin(surface_tilt)
                * np.cos(
                    azimuth_difference_series_array[
                        mask_potentially_sunlit_surface_series
                    ]
                )
                / (
                    0.1
                    - 0.008
                    * solar_altitude_series.radians[
                        mask_potentially_sunlit_surface_series
                    ]
                )
            )

    diffuse_inclined_irradiance_series = np.nan_to_num(
        diffuse_inclined_irradiance_series, nan=0
    )
    if apply_reflectivity_factor:
        diffuse_irradiance_reflectivity_coefficient = sin(surface_tilt) + (
            pi - surface_tilt - sin(surface_tilt)
        ) / (1 + cos(surface_tilt))
        diffuse_irradiance_reflectivity_factor = calculate_reflectivity_factor_for_nondirect_irradiance(
            indirect_angular_loss_coefficient=diffuse_irradiance_reflectivity_coefficient,
        )
        diffuse_irradiance_reflectivity_factor_series = create_array(
            timestamps.shape,
            dtype=dtype,
            init_method=diffuse_irradiance_reflectivity_factor,
            backend=array_backend,
        )
        diffuse_inclined_irradiance_series *= (
            diffuse_irradiance_reflectivity_factor_series
        )

        # for the output dictionary
        diffuse_inclined_irradiance_before_reflectivity_series = where(
            diffuse_irradiance_reflectivity_factor_series != 0,
            diffuse_inclined_irradiance_series
            / diffuse_irradiance_reflectivity_factor_series,
            0,
        )

    out_of_range = (
        diffuse_inclined_irradiance_series < LOWER_PHYSICALLY_POSSIBLE_LIMIT
    ) | (diffuse_inclined_irradiance_series > UPPER_PHYSICALLY_POSSIBLE_LIMIT)
    if out_of_range.any():
        out_of_range_values = diffuse_inclined_irradiance_series[out_of_range]
        stub_array = np.full(out_of_range.shape, -1, dtype=int)
        index_array = np.arange(len(out_of_range))
        out_of_range_indices = np.where(out_of_range, index_array, stub_array)
        warning = (
            f"{WARNING_OUT_OF_RANGE_VALUES} in [code]diffuse_inclined_irradiance_series[/code] :\n{diffuse_inclined_irradiance_series[out_of_range]}"
        )
        warning_unstyled = (
            f"\n"
            f"{WARNING_OUT_OF_RANGE_VALUES} "
            f"[{LOWER_PHYSICALLY_POSSIBLE_LIMIT}, {UPPER_PHYSICALLY_POSSIBLE_LIMIT}]"
            f" in diffuse_inclined_irradiance_series : "
            f"{out_of_range_values}"
            f"\n"
        )
        warning = (
            f"\n"
            f"{WARNING_OUT_OF_RANGE_VALUES} "
            f"[{LOWER_PHYSICALLY_POSSIBLE_LIMIT}, {UPPER_PHYSICALLY_POSSIBLE_LIMIT}]"
            f" in [code]diffuse_inclined_irradiance_series[/code] : "
            f"{out_of_range_values}"
            f"\n"
        )
        logger.warning(warning_unstyled, alt=warning)

    # Building the output dictionary ========================================

    components_container = {
        "Metadata": lambda: {
            POSITION_ALGORITHM_COLUMN_NAME: solar_altitude_series.position_algorithm,
            TIME_ALGORITHM_COLUMN_NAME: solar_altitude_series.timing_algorithm,
            SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
            PERIGEE_OFFSET_COLUMN_NAME: perigee_offset,
            ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_correction_factor,
        },
        "Diffuse Irradiance": lambda: {
            TITLE_KEY_NAME: DIFFUSE_INCLINED_IRRADIANCE,
            DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME: diffuse_inclined_irradiance_series,
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
        },  # if verbose > 0 else {},
        "extended_2": lambda: (
            {
                REFLECTIVITY_COLUMN_NAME: calculate_reflectivity_effect(
                    irradiance=diffuse_inclined_irradiance_before_reflectivity_series,
                    reflectivity=diffuse_irradiance_reflectivity_factor_series,
                ),
                REFLECTIVITY_PERCENTAGE_COLUMN_NAME: calculate_reflectivity_effect_percentage(
                    irradiance=diffuse_inclined_irradiance_before_reflectivity_series,
                    reflectivity=diffuse_irradiance_reflectivity_factor_series,
                ),
            }
            if verbose > 6 and apply_reflectivity_factor
            else {}
        ),
        "extended": lambda: (
            {
                # REFLECTIVITY_FACTOR_COLUMN_NAME: where(diffuse_irradiance_loss_factor_series <= 0, 0, (1 - diffuse_irradiance_loss_factor_series)),
                REFLECTIVITY_FACTOR_COLUMN_NAME: diffuse_irradiance_reflectivity_factor_series,
                DIFFUSE_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: diffuse_inclined_irradiance_before_reflectivity_series,
                # } if verbose > 1 and apply_reflectivity_factor else {},
            }
            if apply_reflectivity_factor
            else {}
        ),
        "Surface position": lambda: (
            {
                SURFACE_ORIENTATION_COLUMN_NAME: convert_float_to_degrees_if_requested(
                    surface_orientation, angle_output_units
                ),
                SURFACE_TILT_COLUMN_NAME: convert_float_to_degrees_if_requested(
                    surface_tilt, angle_output_units
                ),
                ANGLE_UNITS_COLUMN_NAME: angle_output_units,
                TITLE_KEY_NAME: DIFFUSE_INCLINED_IRRADIANCE + " & relevant components",
                DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME: diffuse_horizontal_irradiance_series,
                DIFFUSE_CLEAR_SKY_IRRADIANCE_COLUMN_NAME: diffuse_sky_irradiance_series,
            }
            if verbose > 2
            else {}
        ),
        "even_more_extended": lambda: (
            {
                TERM_N_COLUMN_NAME: n_series,
                KB_RATIO_COLUMN_NAME: kb_series,
                AZIMUTH_DIFFERENCE_COLUMN_NAME: getattr(
                    azimuth_difference_series_array, angle_output_units, np.nan
                ),
                AZIMUTH_COLUMN_NAME: getattr(
                    solar_azimuth_series_array, angle_output_units, NOT_AVAILABLE
                ),
                ALTITUDE_COLUMN_NAME: (
                    getattr(solar_altitude_series, angle_output_units)
                    if solar_altitude_series
                    else None
                ),  # Altitude should be always there! If not, something is wrong.  This is why this entry does not need the NOT_AVAILABLE fallback.
            }
            if verbose > 3
            else {}
        ),
        "and_even_more_extended": lambda: (
            {
                GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME: global_horizontal_irradiance_series,
                DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
                EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME: extraterrestrial_horizontal_irradiance_series,
                EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME: extraterrestrial_normal_irradiance_series.value,
                LINKE_TURBIDITY_COLUMN_NAME: linke_turbidity_factor_series.value,
            }
            if verbose > 4
            else {}
        ),
        "extra": lambda: (
            {
                INCIDENCE_COLUMN_NAME: (
                    getattr(solar_incidence_series, angle_output_units, NOT_AVAILABLE)
                    if solar_incidence_series
                    else None
                ),
                INCIDENCE_ALGORITHM_COLUMN_NAME: solar_incidence_model,
            }
            if verbose > 5
            else {}
        ),
        "out-of-range": lambda: (
            {
                OUT_OF_RANGE_INDICES_COLUMN_NAME: out_of_range,
                OUT_OF_RANGE_INDICES_COLUMN_NAME + " i": out_of_range_indices,
            }
            if out_of_range.any() > 0
            else {}
        ),
        "fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(
                    diffuse_inclined_irradiance_series
                ),
            }
            if fingerprint
            else {}
        ),
    }

    components = {}
    for _, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=diffuse_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
        value=diffuse_inclined_irradiance_series,
        unit=IRRADIANCE_UNIT,
        position_algorithm=solar_altitude_series.position_algorithm,
        timing_algorithm=solar_altitude_series.timing_algorithm,
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        components=components,
    )

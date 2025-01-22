from math import cos, pi, sin
from pathlib import Path
from typing import List
from zoneinfo import ZoneInfo

import numpy as np
from devtools import debug
from numpy import ndarray, where
import numpy
from pandas import DatetimeIndex, Timestamp
from pydantic_numpy import NpNDArray

from pvgisprototype import (
    ExtraterrestrialIrradiance,
    DiffuseIrradiance,
    LinkeTurbidityFactor,
    SurfaceOrientation,
    SurfaceTilt,
    SolarAltitude,
    SolarAzimuth,
    SolarIncidence,
)
from pvgisprototype.algorithms.pvis.diffuse.horizontal import calculate_diffuse_horizontal_irradiance_series_pvgis
from pvgisprototype.algorithms.pvis.diffuse.horizontal_from_external_series import calculate_diffuse_horizontal_component_from_external_series_pvgis
from pvgisprototype.algorithms.pvis.diffuse.term_n import (
    calculate_term_n_series_hofierka,
)
from pvgisprototype.algorithms.pvis.diffuse.sky_irradiance import (
    calculate_diffuse_sky_irradiance_series_hofierka,
)
from pvgisprototype.algorithms.pvis.direct.horizontal import (
    calculate_direct_horizontal_irradiance_series_pvgis,
)
from pvgisprototype.algorithms.pvis.extraterrestrial import (
    calculate_extraterrestrial_normal_irradiance_series_pvgis,
)
from pvgisprototype.api.irradiance.limits import (
    LOWER_PHYSICALLY_POSSIBLE_LIMIT,
    UPPER_PHYSICALLY_POSSIBLE_LIMIT,
)
from pvgisprototype.api.irradiance.reflectivity import (
    calculate_reflectivity_factor_for_nondirect_irradiance,
)
from pvgisprototype.api.position.models import (
    SOLAR_TIME_ALGORITHM_DEFAULT,
    ShadingState,
    SolarTimeModel,
)
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DIFFUSE_INCLINED_IRRADIANCE,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_UNIT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    NOT_AVAILABLE,
    PERIGEE_OFFSET,
    RADIANS,
    SOLAR_CONSTANT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    TERM_N_IN_SHADE,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.core.arrays import create_array
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
def calculate_diffuse_inclined_irradiance_series_pvgis(
    longitude: float,
    latitude: float,
    elevation: float,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    surface_tilt_horizontally_flat_panel_threshold: float = SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    timestamps: DatetimeIndex | None = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo | None = ZoneInfo('UTC'),
    global_horizontal_irradiance_series: ndarray | None = None,
    direct_horizontal_irradiance_series: ndarray | None = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_reflectivity_factor: bool = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_altitude_series: SolarAltitude | None = None,
    solar_azimuth_series: SolarAzimuth | None = NOT_AVAILABLE,
    solar_incidence_series: SolarIncidence | None = None,
    surface_in_shade_series: NpNDArray | None = None,
    shading_states: List[ShadingState] = [ShadingState.all],
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> DiffuseIrradiance:
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
    # ----------------------------------- Diffuse Horizontal Irradiance -- vvv
    # If the global & direct input are already time series in form of arrays
    # calculate the diffuse horizontal irradiance
    if isinstance(global_horizontal_irradiance_series, ndarray) and isinstance(
        direct_horizontal_irradiance_series, ndarray
    ):
        logger.info(
            ":information: Calculating clear-sky diffuse horizontal irradiance from external time series ...",
            alt = ":information: [bold]Calculating[/bold] clear-sky diffuse horizontal irradiance from external time series ..."
        )

        # --------------------------------------------------------------------
        # While the following operation is a simple subtraction,
        # i.e. global - direct
        # we use the PVGIS-native data model returned by the function in question
        # to make use of its rich attributes
        #
        diffuse_horizontal_irradiance_series = calculate_diffuse_horizontal_component_from_external_series_pvgis(
            global_horizontal_irradiance_series=global_horizontal_irradiance_series,
            direct_horizontal_irradiance_series=direct_horizontal_irradiance_series,
            # longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
            # latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
            # timestamps=timestamps,
            # neighbor_lookup=neighbor_lookup,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            fingerprint=fingerprint,
        )
        #
        # Attention :
        # This obect carries an _unset_ extraterrestrial_normal_irradiance array
        # -- Do Not Use It in the following calculations for the diffuse inclined irradiance component.
        # --------------------------------------------------------------------

    else:  # model the diffuse horizontal irradiance
        if verbose > 0:
            logger.info(
                ":information: Modelling clear-sky diffuse horizontal irradiance ...",
                alt=":information: [bold]Modelling[/bold] clear-sky diffuse horizontal irradiance ...",
            )
        # create a placeholder array for global horizontal irradiance
        global_horizontal_irradiance_series = create_array(
            timestamps.shape, dtype=dtype, init_method=np.nan, backend=array_backend
        )

        # in which case, however and if NOT read from external series already,
        # we need the direct component for the kb series
        direct_horizontal_irradiance_series = (
            calculate_direct_horizontal_irradiance_series_pvgis(
                elevation=elevation,
                timestamps=timestamps,
                solar_altitude_series=solar_altitude_series,
                surface_in_shade_series=surface_in_shade_series.value,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                solar_constant=solar_constant,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
                fingerprint=fingerprint,
            )
        ).value  # Important !  Or if not used here, then wherever required !
        diffuse_horizontal_irradiance_series = (
            calculate_diffuse_horizontal_irradiance_series_pvgis(
                timestamps=timestamps,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                solar_altitude_series=solar_altitude_series,
                solar_constant=solar_constant,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
                fingerprint=fingerprint,
            )
        )
    #
    # ----------------------------------- Diffuse Horizontal Irradiance -- ^^^

    # At this point, the diffuse_horizontal_irradiance_series are either :
    # calculated from external time series  Or  modelled

    # Initialise shading_state_series to avoid the "UnboundLocalError"
    shading_state_series = create_array(
        timestamps.shape, dtype='object', init_method="empty", backend=array_backend
    )

    if surface_tilt <= surface_tilt_horizontally_flat_panel_threshold:
        diffuse_inclined_irradiance_series = np.copy(
            diffuse_horizontal_irradiance_series.value
        )
        # to not break the output !
        diffuse_sky_irradiance_series = NOT_AVAILABLE
        n_series = NOT_AVAILABLE
        kb_series = NOT_AVAILABLE
        azimuth_difference_series = NOT_AVAILABLE
        solar_incidence_series = SolarIncidence()
        extraterrestrial_horizontal_irradiance_series = ExtraterrestrialIrradiance(
            value=numpy.full(timestamps.shape, "Unset", "object"),
            unit=None,
            day_angle=None,
            solar_constant=None,
            perigee_offset=None,
            eccentricity_correction_factor=None,
            distance_correction_factor=None,
        )
        extraterrestrial_normal_irradiance_series = ExtraterrestrialIrradiance(
            value=numpy.full(timestamps.shape, "Unset", "object"),
            unit=None,
            day_angle=None,
            solar_constant=None,
            perigee_offset=None,
            eccentricity_correction_factor=None,
            distance_correction_factor=None,
        )

    else:  # tilted (or inclined) surface
        # Note: in PVGIS: if surface_orientation != 'UNDEF' and surface_tilt != 0:
        # --------------------------------------------------- Is this safe ? -

        # Calculate or get quantities required : ---------------------------- >>> >>> >>>
        # 1. to model the diffuse horizontal irradiance [optional]
        # 2. to calculate the diffuse sky ... to consider shaded, sunlit and potentially sunlit surfaces
        #

        extraterrestrial_normal_irradiance_series = (
            calculate_extraterrestrial_normal_irradiance_series_pvgis(
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
        extraterrestrial_horizontal_irradiance_series = ExtraterrestrialIrradiance(
            value=extraterrestrial_normal_irradiance_series.value
            * np.sin(solar_altitude_series.radians),
            unit=None,
            day_angle=None,
            solar_constant=None,
            perigee_offset=None,
            eccentricity_correction_factor=None,
            distance_correction_factor=None,
        )
        extraterrestrial_horizontal_irradiance_series.value[solar_altitude_series.radians < 0] = (
            0  # In the context of PVGIS, does it make sense to have negative extraterrestrial horizontal irradiance
        )
        #
        # Calculate quantities required : ---------------------------- <<< <<< <<<

        with np.errstate(divide="ignore", invalid="ignore"):
            kb_series = (  # proportion between direct and extraterrestrial
                direct_horizontal_irradiance_series
                / extraterrestrial_horizontal_irradiance_series.value
            )
        n_series = calculate_term_n_series_hofierka(
            kb_series,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
        )
        diffuse_sky_irradiance_series = where(
            np.isnan(n_series),  # handle NaN cases
            0,
            calculate_diffuse_sky_irradiance_series_hofierka(
                n_series=n_series,
                surface_tilt=surface_tilt,
            ),
        )

        # prepare size of output array!

        diffuse_inclined_irradiance_series = create_array(
            timestamps.shape, dtype=dtype, init_method="zeros", backend=array_backend
        )

        # prepare cases : surfaces in shade, sunlit, potentially sunlit

        from pvgisprototype.api.position.models import select_models
        shading_states = select_models(
            ShadingState, shading_states
        )  # Using a callback fails!

        if ShadingState.in_shade in shading_states:
            #  ----------------------------------------------------- Review Me
            mask_surface_in_shade_series = np.logical_or(
                # np.sin(solar_incidence_series.radians) < 0,  # in shade
                # will never be True ! when negative incidence angles set to 0 !
                solar_incidence_series.radians < 0,  # in shade
                # ---------------------------------------------- Review Me ---
                # solar_altitude_series.radians >= 0,  # yet there is ambient light
                surface_in_shade_series.value  # pre-calculated in-shade moments 
            )
            # Is this the _complementary_ incidence angle series ?
            #  Review Me -----------------------------------------------------
            if np.any(mask_surface_in_shade_series):
                shading_state_series[mask_surface_in_shade_series] = ['In-shade']
                logger.info(
                    f"Shading state series :\n{shading_state_series}",
                    alt=f"[bold]Shading state[/bold] series :\n{shading_state_series}",
                )
                diffuse_sky_irradiance_series[mask_surface_in_shade_series] = (
                    calculate_diffuse_sky_irradiance_series_hofierka(
                        n_series=np.full(len(timestamps), TERM_N_IN_SHADE),
                        surface_tilt=surface_tilt,
                    )[mask_surface_in_shade_series]
                )
                diffuse_inclined_irradiance_series[mask_surface_in_shade_series] = (
                    diffuse_horizontal_irradiance_series.value[mask_surface_in_shade_series]
                    * diffuse_sky_irradiance_series[mask_surface_in_shade_series]
                )

        if ShadingState.sunlit in shading_states:
            mask_sunlit_surface_series = np.logical_and(
                solar_altitude_series.radians >= 0.1,  # or >= 5.7 degrees
                shading_state_series == None  # operate only on unset elements
            )

            # else:  # sunlit surface and non-overcast sky
            #     # ----------------------------------------------------------------
            #     solar_azimuth_series = None ?
            #     # ----------------------------------------------------------------
            if np.any(mask_sunlit_surface_series):
                shading_state_series[mask_sunlit_surface_series] = 'Sunlit'
                logger.info(
                    f"Shading state series including sunlit :\n{shading_state_series}",
                    alt=f"Shading state series including [bold yellow]sunlit[/bold yellow] :\n{shading_state_series}",
                )
                diffuse_inclined_irradiance_series[
                    mask_sunlit_surface_series
                ] = diffuse_horizontal_irradiance_series.value[mask_sunlit_surface_series] * (
                    diffuse_sky_irradiance_series[mask_sunlit_surface_series]
                    * (1 - kb_series[mask_sunlit_surface_series])
                    + kb_series[mask_sunlit_surface_series]
                    * np.sin(
                        solar_incidence_series.radians[mask_sunlit_surface_series]
                    )  # Should be the _complementary_ incidence angle!
                    / np.sin(solar_altitude_series.radians[mask_sunlit_surface_series])
                )

        azimuth_difference_series = NOT_AVAILABLE  # not always required, set to avoid UnboundLocalError!
        if ShadingState.potentially_sunlit in shading_states:
            mask_potentially_sunlit_surface_series = np.logical_and(
                    solar_altitude_series.radians > 0,  #  sun above horizon
                solar_altitude_series.radians < 0.1,  #  radians or < 5.7 degrees
                shading_state_series == None  # operate only on unset elements
            )
            # else:  # if solar altitude < 0.1 : potentially sunlit surface series
            if np.any(mask_potentially_sunlit_surface_series):
                shading_state_series[mask_potentially_sunlit_surface_series] = 'Potentially Sunlit'
                logger.info(
                    f"Shading state series including potentially-sunlit :\n{shading_state_series}",
                    alt=f"[bold]Shading state[/bold] series including [bold orange]potentially-sunlit[/bold orange] :\n{shading_state_series}",
                )
                # requires the solar azimuth
                # Normalize the azimuth difference to be within the range -pi to pi
                # A0 : solar azimuth _measured from East_ in radians
                # ALN : angle between the vertical surface containing the normal to the
                #   surface and vertical surface passing through the centre of the solar
                #   disc [rad]
                if isinstance(surface_orientation, SurfaceOrientation): # FIXME This should always be SurfaceOrientation instance and MUST BE FIXED with pydantic!
                    surface_orientation = surface_orientation.value
                
                azimuth_difference_series = (
                        solar_azimuth_series.value - surface_orientation
                    )
                azimuth_difference_series = np.arctan2(
                    np.sin(azimuth_difference_series),
                    np.cos(azimuth_difference_series),
                )
                diffuse_inclined_irradiance_series[
                    mask_potentially_sunlit_surface_series
                ] = diffuse_horizontal_irradiance_series.value[
                    mask_potentially_sunlit_surface_series
                ] * (
                    diffuse_sky_irradiance_series[mask_potentially_sunlit_surface_series]
                    * (1 - kb_series[mask_potentially_sunlit_surface_series])
                    + kb_series[mask_potentially_sunlit_surface_series]
                    * sin(surface_tilt)
                    * np.cos(
                        azimuth_difference_series[
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

    # Replace None with a placeholder -- this is important for printing !
    shading_state_series = np.where(
        shading_state_series == None, "Unset", shading_state_series
    )
    # ------------------------------------------------------------------------

    # diffuse_inclined_irradiance_series = np.nan_to_num(
    #     diffuse_inclined_irradiance_series, nan=0
    # )


    EPSILON = 0.1 #1e-10  # Define a small threshold for comparison
    diffuse_irradiance_reflectivity_factor_series = None
    diffuse_inclined_irradiance_before_reflectivity_series = None
    if apply_reflectivity_factor:
        if abs(surface_tilt - pi) < EPSILON:
            surface_tilt -= EPSILON

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
    out_of_range_indices = create_array(
            timestamps.shape, dtype=dtype, init_method=np.nan, backend=array_backend
    )
    if out_of_range.any():
        out_of_range_values = diffuse_inclined_irradiance_series[out_of_range]
        stub_array = np.full(out_of_range.shape, -1, dtype=int)
        index_array = np.arange(len(out_of_range))
        out_of_range_indices = np.where(out_of_range, index_array, stub_array)
        warning = f"{WARNING_OUT_OF_RANGE_VALUES} in [code]diffuse_inclined_irradiance_series[/code] :\n{diffuse_inclined_irradiance_series[out_of_range]}"
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

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=diffuse_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return DiffuseIrradiance(
        value=diffuse_inclined_irradiance_series,
        unit=IRRADIANCE_UNIT,
        title=DIFFUSE_INCLINED_IRRADIANCE,
        solar_radiation_model=HOFIERKA_2002,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_indices,
        global_horizontal_irradiance=global_horizontal_irradiance_series,
        direct_horizontal_irradiance=direct_horizontal_irradiance_series,
        extraterrestrial_horizontal_irradiance=extraterrestrial_horizontal_irradiance_series.value,
        extraterrestrial_normal_irradiance=extraterrestrial_normal_irradiance_series.value,
        linke_turbidity_factor=linke_turbidity_factor_series,
        before_reflectivity=diffuse_inclined_irradiance_before_reflectivity_series if diffuse_inclined_irradiance_before_reflectivity_series is not None else NOT_AVAILABLE,
        reflectivity_factor= diffuse_irradiance_reflectivity_factor_series if diffuse_inclined_irradiance_before_reflectivity_series is not None else NOT_AVAILABLE,
        shading_states=shading_states,
        shading_state_series=shading_state_series,
        diffuse_horizontal_irradiance=diffuse_horizontal_irradiance_series.value,
        diffuse_sky_irradiance=diffuse_sky_irradiance_series,
        term_n=n_series,
        kb_ratio=kb_series,
        solar_position_algorithm=solar_altitude_series.position_algorithm,
        solar_timing_algorithm=solar_altitude_series.timing_algorithm,
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        solar_altitude=solar_altitude_series,
        solar_azimuth=solar_azimuth_series,
        azimuth_difference=azimuth_difference_series,
        solar_incidence=solar_incidence_series,
        data_source=HOFIERKA_2002,
    )

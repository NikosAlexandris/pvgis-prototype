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
from math import cos, pi, sin
from typing import List
from zoneinfo import ZoneInfo

import numpy as np
from devtools import debug
from numpy import errstate, ndarray, where
from pandas import DatetimeIndex, Timestamp
from pydantic_numpy import NpNDArray

from pvgisprototype import (
    ExtraterrestrialNormalIrradiance,
    ExtraterrestrialHorizontalIrradiance,
    DiffuseSkyReflectedInclinedIrradiance,
    LinkeTurbidityFactor,
    SurfaceOrientation,
    SurfaceTilt,
    SolarAltitude,
    SolarAzimuth,
    SolarIncidence,
)
from pvgisprototype.algorithms.hofierka.irradiance.diffuse.clear_sky.horizontal import calculate_clear_sky_diffuse_horizontal_irradiance_hofierka
from pvgisprototype.algorithms.muneer.irradiance.diffuse.in_shade import calculate_diffuse_inclined_irradiance_in_shade
from pvgisprototype.algorithms.muneer.irradiance.diffuse.potentially_sunlit import calculate_diffuse_inclined_irradiance_potentially_sunlit
from pvgisprototype.algorithms.muneer.irradiance.diffuse.sunlit import calculate_diffuse_inclined_irradiance_sunlit
from pvgisprototype.algorithms.muneer.irradiance.diffuse.term_n import (
    calculate_term_n_series_hofierka,
)
from pvgisprototype.algorithms.muneer.irradiance.diffuse.sky_irradiance import (
    calculate_diffuse_sky_irradiance_series_hofierka,
)
from pvgisprototype.algorithms.hofierka.irradiance.direct.clear_sky.horizontal import (
    calculate_clear_sky_direct_horizontal_irradiance_hofierka,
)
from pvgisprototype.algorithms.hofierka.irradiance.extraterrestrial.normal import (
    calculate_extraterrestrial_normal_irradiance_hofierka,
)
from pvgisprototype.algorithms.hofierka.irradiance.extraterrestrial.horizontal import calculate_extraterrestrial_horizontal_irradiance_series_hofierka
from pvgisprototype.algorithms.martin_ruiz.reflectivity import (
    calculate_reflectivity_effect,
    calculate_reflectivity_factor_for_nondirect_irradiance,
)
from pvgisprototype.api.position.models import (
    ShadingState,
)
from pvgisprototype.constants import (
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    NOT_AVAILABLE,
    ECCENTRICITY_PHASE_OFFSET,
    SOLAR_CONSTANT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    TERM_N_IN_SHADE,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.core.arrays import create_array
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.validation.values import identify_values_out_of_range
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


MINIMAL_DIFFERENCE_THRESHOLD = 0.1 #1e-10  # Define a small threshold for comparison


@log_function_call
@custom_cached
def calculate_clear_sky_diffuse_inclined_irradiance_muneer(
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
    solar_azimuth_series: SolarAzimuth | None = SolarAzimuth(),
    solar_incidence_series: SolarIncidence | None = None,
    surface_in_shade_series: NpNDArray | None = None,
    shading_states: List[ShadingState] = [ShadingState.all],
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> DiffuseSkyReflectedInclinedIrradiance:
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
    if (
        global_horizontal_irradiance_series is not None
        and direct_horizontal_irradiance_series is not None
    ):
        logger.error(
            ":information: The global_horizontal_irradiance and/or direct_horizontal_irradiance inputs should be None at this point !",
            alt = ":information: [bold red]The [code]global_horizontal_irradiance[/code] and/or [code]direct_horizontal_irradiance[/code] inputs should be [code]None[/code] at this point ![/bold red]",
        )
        raise ValueError(
            ":information: The `global_horizontal_irradiance` and/or `direct_horizontal_irradiance` inputs should be `None` at this point !",
        )

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
            calculate_clear_sky_direct_horizontal_irradiance_hofierka(
                elevation=elevation,
                timestamps=timestamps,
                solar_altitude_series=solar_altitude_series,
                surface_in_shade_series=surface_in_shade_series,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                solar_constant=solar_constant,
                eccentricity_phase_offset=eccentricity_phase_offset,
                eccentricity_amplitude=eccentricity_amplitude,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
            )
        )
        diffuse_horizontal_irradiance_series = (
            calculate_clear_sky_diffuse_horizontal_irradiance_hofierka(
                timestamps=timestamps,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                solar_altitude_series=solar_altitude_series,
                solar_constant=solar_constant,
                eccentricity_phase_offset=eccentricity_phase_offset,
                eccentricity_amplitude=eccentricity_amplitude,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
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
    nan_series = create_array(
        timestamps.shape, dtype=dtype, init_method=np.nan, backend=array_backend
    )
    unset_series = create_array(
        timestamps.shape, dtype=dtype, init_method="unset", backend=array_backend
    )
    # np.full(timestamps.shape, "Unset", "object")

    if surface_tilt <= surface_tilt_horizontally_flat_panel_threshold:
        if verbose > 0:
            logger.info(
                ":information: Modelling clear-sky diffuse inclined irradiance for a horizontally flat panel...",
                alt=":information: [bold]Modelling[/bold] clear-sky diffuse inclined irradiance for a horizontally flat panel...",
            )
        diffuse_inclined_irradiance_series = np.copy(
            diffuse_horizontal_irradiance_series.value
        )
        # to not break the output !
        diffuse_sky_irradiance_series = unset_series
        n_series = unset_series
        kb_series = unset_series
        azimuth_difference_series = unset_series
        solar_incidence_series = SolarIncidence(
            value=unset_series,
            incidence_algorithm=NOT_AVAILABLE,
            definition=NOT_AVAILABLE,
            azimuth_origin=NOT_AVAILABLE,
        )
        extraterrestrial_normal_irradiance_series = ExtraterrestrialNormalIrradiance(
            value=unset_series,
            unit=NOT_AVAILABLE,
            day_angle=unset_series,
            solar_constant=None,
            eccentricity_phase_offset=None,
            eccentricity_amplitude=None,
            distance_correction_factor=None,
        )
        extraterrestrial_horizontal_irradiance_series = ExtraterrestrialHorizontalIrradiance(
            value=unset_series,
            unit=NOT_AVAILABLE,
            day_angle=unset_series,
            solar_constant=None,
            eccentricity_phase_offset=None,
            eccentricity_amplitude=None,
            distance_correction_factor=None,
        )

    else:  # tilted (or inclined) surface
        # Note: in PVGIS: if surface_orientation != 'UNDEF' and surface_tilt != 0:
        # --------------------------------------------------- Is this safe ? -

        # Calculate or get quantities required : ---------------------------- >>> >>> >>>
        # 1. to model the diffuse horizontal irradiance [optional]
        # 2. to calculate the diffuse sky ... to consider shaded, sunlit and potentially sunlit surfaces
        #
        if verbose > 0:
            logger.info(
                ":information: Modelling clear-sky diffuse inclined irradiance for a tilted panel...",
                alt=":information: [bold]Modelling[/bold] clear-sky diffuse inclined irradiance for a tilted panel...",
            )

        extraterrestrial_normal_irradiance_series = (
            calculate_extraterrestrial_normal_irradiance_hofierka(
                timestamps=timestamps,
                solar_constant=solar_constant,
                eccentricity_phase_offset=eccentricity_phase_offset,
                eccentricity_amplitude=eccentricity_amplitude,
                dtype=dtype,
                array_backend=array_backend,
                verbose=0,  # no verbosity here by choice!
                log=log,
            )
        )
        extraterrestrial_horizontal_irradiance_series = calculate_extraterrestrial_horizontal_irradiance_series_hofierka(
            extraterrestrial_normal_irradiance=extraterrestrial_normal_irradiance_series,
            solar_altitude_series=solar_altitude_series,
        )
        #
        # Calculate quantities required : ---------------------------- <<< <<< <<<

        with np.errstate(divide="ignore", invalid="ignore"):
            kb_series = (  # proportion between direct and extraterrestrial
                direct_horizontal_irradiance_series.value
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

        # from pvgisprototype.api.position.models import select_models
        # shading_states = select_models(
        #     ShadingState, shading_states
        # )  # Using a callback fails!

        diffuse_inclined_irradiance_series = calculate_diffuse_inclined_irradiance_in_shade(
            # mask_surface_in_shade_series=mask_surface_in_shade_series,
            solar_incidence=solar_incidence_series,
            surface_in_shade=surface_in_shade_series,
            shading_states=shading_states,
            shading_state_series=shading_state_series,
            diffuse_sky_irradiance=diffuse_sky_irradiance_series,
            timestamps=timestamps,
            surface_tilt=surface_tilt,
            diffuse_inclined_irradiance=diffuse_inclined_irradiance_series,
            diffuse_horizontal_irradiance=diffuse_horizontal_irradiance_series,
        )

        diffuse_inclined_irradiance_series = calculate_diffuse_inclined_irradiance_sunlit(
            solar_incidence=solar_incidence_series,
            shading_states=shading_states,
            solar_altitude=solar_altitude_series,
            shading_state_series=shading_state_series,
            diffuse_sky_irradiance=diffuse_sky_irradiance_series,
            kb_series=kb_series,
            diffuse_inclined_irradiance=diffuse_inclined_irradiance_series,
            diffuse_horizontal_irradiance=diffuse_horizontal_irradiance_series,
        )
        #
        azimuth_difference_series = NOT_AVAILABLE  # not always required, set to avoid UnboundLocalError!
        #
        diffuse_inclined_irradiance_series = calculate_diffuse_inclined_irradiance_potentially_sunlit(
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            solar_azimuth=solar_azimuth_series,
            shading_states=shading_states,
            solar_altitude=solar_altitude_series,
            shading_state_series=shading_state_series,
            diffuse_sky_irradiance=diffuse_sky_irradiance_series,
            kb_series=kb_series,
            diffuse_inclined_irradiance=diffuse_inclined_irradiance_series,
            diffuse_horizontal_irradiance=diffuse_horizontal_irradiance_series,
        )

    # Replace None with a placeholder -- this is important for printing !
    shading_state_series = np.where(
        shading_state_series == None, "Unset", shading_state_series
    )
    # ------------------------------------------------------------------------

    # diffuse_inclined_irradiance_series = np.nan_to_num(
    #     diffuse_inclined_irradiance_series, nan=0
    # )

    diffuse_irradiance_reflectivity_coefficient = None
    diffuse_inclined_irradiance_reflectivity_factor_series = nan_series
    diffuse_inclined_irradiance_before_reflectivity_series = nan_series

    if apply_reflectivity_factor:
        if abs(surface_tilt - pi) < MINIMAL_DIFFERENCE_THRESHOLD:
            surface_tilt -= MINIMAL_DIFFERENCE_THRESHOLD

        # Get the reflectivity coefficient
        diffuse_irradiance_reflectivity_coefficient = sin(surface_tilt) + (
            pi - surface_tilt - sin(surface_tilt)
        ) / (1 + cos(surface_tilt))
        diffuse_irradiance_reflectivity_factor = calculate_reflectivity_factor_for_nondirect_irradiance(
            indirect_angular_loss_coefficient=diffuse_irradiance_reflectivity_coefficient,
        )

        # Get the reflectivity factor from ...
        diffuse_inclined_irradiance_reflectivity_factor_series = create_array(
            timestamps.shape,
            dtype=dtype,
            init_method=diffuse_irradiance_reflectivity_factor,
            backend=array_backend,
        )

        # Apply the reflectivity factor
        diffuse_inclined_irradiance_series *= (
            diffuse_inclined_irradiance_reflectivity_factor_series
        )

        # avoid copying to save memory and time ... ? ----------------- Is this safe ? -
        with errstate(divide="ignore", invalid="ignore"):
            # this quantity is exclusively generated for the output dictionary !
            diffuse_inclined_irradiance_before_reflectivity_series = where(
                diffuse_inclined_irradiance_reflectivity_factor_series != 0,
                diffuse_inclined_irradiance_series
                / diffuse_inclined_irradiance_reflectivity_factor_series,
                0,
            )
        # ------------------------------------------------------------------------------

    out_of_range, out_of_range_index = identify_values_out_of_range(
        series=diffuse_inclined_irradiance_series,
        shape=timestamps.shape,
        data_model=DiffuseSkyReflectedInclinedIrradiance(),
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=diffuse_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return DiffuseSkyReflectedInclinedIrradiance(
        value=diffuse_inclined_irradiance_series,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_index,
        #
        global_horizontal_irradiance=global_horizontal_irradiance_series,
        direct_horizontal_irradiance=direct_horizontal_irradiance_series,
        diffuse_horizontal_irradiance=diffuse_horizontal_irradiance_series,
        extraterrestrial_horizontal_irradiance=extraterrestrial_horizontal_irradiance_series,
        #
        extraterrestrial_normal_irradiance=extraterrestrial_normal_irradiance_series,
        #
        reflected=calculate_reflectivity_effect(
                irradiance=diffuse_inclined_irradiance_before_reflectivity_series,
                reflectivity_factor=diffuse_inclined_irradiance_reflectivity_factor_series,
            ),
        reflectivity_factor=diffuse_inclined_irradiance_reflectivity_factor_series,
        reflectivity_coefficient=diffuse_irradiance_reflectivity_coefficient,
        value_before_reflectivity=diffuse_inclined_irradiance_before_reflectivity_series,
        #
        diffuse_sky_irradiance=diffuse_sky_irradiance_series,
        term_n=n_series,
        kb_ratio=kb_series,
        #
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        surface_tilt_threshold=surface_tilt_horizontally_flat_panel_threshold,
        #
        surface_in_shade=surface_in_shade_series,
        solar_incidence=solar_incidence_series,
        shading_state=shading_state_series,
        solar_altitude=solar_altitude_series,
        solar_azimuth=solar_azimuth_series,
        azimuth_origin=solar_azimuth_series.origin,
        azimuth_difference=azimuth_difference_series,
        #
        solar_incidence_model=solar_incidence_series.algorithm,
        solar_incidence_definition=solar_incidence_series.definition,
        shading_states=shading_states,
    )

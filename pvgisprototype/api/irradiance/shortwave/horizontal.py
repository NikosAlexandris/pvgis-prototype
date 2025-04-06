"""
API module to calculate the global (shortwave) irradiance over a
location for a period in time.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
from devtools import debug
from xarray import DataArray

from pvgisprototype import Irradiance, LinkeTurbidityFactor
from pvgisprototype.algorithms.pvis.diffuse.altitude import (
    calculate_diffuse_solar_altitude_function_series_hofierka,
)
from pvgisprototype.algorithms.pvis.diffuse.horizontal import calculate_diffuse_horizontal_irradiance_series_pvgis
from pvgisprototype.algorithms.pvis.diffuse.transmission_function import (
    calculate_diffuse_transmission_function_series_hofierka,
)
from pvgisprototype.api.irradiance.diffuse.horizontal import calculate_diffuse_horizontal_irradiance_series
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
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.models import ShadingModel, SolarPositionModel, SolarTimeModel
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ALTITUDE_COLUMN_NAME,
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR,
    EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    GLOBAL_HORIZONTAL_IRRADIANCE,
    GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_UNIT,
    LINKE_TURBIDITY_COLUMN_NAME,
    LOG_LEVEL_DEFAULT,
    PERIGEE_OFFSET,
    RADIANS,
    RADIATION_MODEL_COLUMN_NAME,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    TITLE_KEY_NAME,
    VALIDATE_OUTPUT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.core.hashing import generate_hash


@log_function_call
def calculate_global_horizontal_irradiance_series(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: datetime | None = None,
    timezone: ZoneInfo | None = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = None,  # Changed this to np.ndarray
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
):
    """
    Calculate the global horizontal irradiance (GHI)

    The global horizontal irradiance represents the total amount of shortwave
    radiation received from above by a surface horizontal to the ground. It
    includes both the direct and the diffuse solar radiation.
    """
    if verbose > 0:
        logger.info(
            ":information: Modelling direct horizontal irradiance...",
            alt=":information: [bold][magenta]Modelling[/magenta] direct horizontal irradiance[/bold]..."
        )
    direct_horizontal_irradiance_series = calculate_direct_horizontal_irradiance_series(
        longitude=longitude,  # required by some of the solar time algorithms
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        solar_time_model=solar_time_model,
        solar_position_model=solar_position_model,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        horizon_profile=horizon_profile,
        shading_model=shading_model,
        angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        validate_output=validate_output,
        verbose=0,  # by choice !
        log=log,
        fingerprint=fingerprint,
    )#.value  # Important !
    # extraterrestrial_normal_irradiance_series = (
    #     calculate_extraterrestrial_normal_irradiance_series(
    #         timestamps=timestamps,
    #         solar_constant=solar_constant,
    #         perigee_offset=perigee_offset,
    #         eccentricity_correction_factor=eccentricity_correction_factor,
    #         dtype=dtype,
    #         array_backend=array_backend,
    #         verbose=0,  # no verbosity here by choice!
    #         log=log,
    #     )
    # )
    # # extraterrestrial on a horizontal surface requires the solar altitude
    # solar_altitude_series = model_solar_altitude_series(
    #     longitude=longitude,
    #     latitude=latitude,
    #     timestamps=timestamps,
    #     timezone=timezone,
    #     solar_position_model=solar_position_model,
    #     apply_atmospheric_refraction=apply_atmospheric_refraction,
    #     refracted_solar_zenith=refracted_solar_zenith,
    #     solar_time_model=solar_time_model,
    #     perigee_offset=perigee_offset,
    #     eccentricity_correction_factor=eccentricity_correction_factor,
    #     angle_output_units=angle_output_units,
    #     dtype=dtype,
    #     array_backend=array_backend,
    #     verbose=0,
    #     log=log,
    # )
    # diffuse_horizontal_irradiance_series = (
    #     extraterrestrial_normal_irradiance_series.value
    #     * calculate_diffuse_transmission_function_series_hofierka(linke_turbidity_factor_series)
    #     * calculate_diffuse_solar_altitude_function_series_hofierka(
    #         solar_altitude_series, linke_turbidity_factor_series
    #     )
    # )
    diffuse_horizontal_irradiance_series = (
        calculate_diffuse_horizontal_irradiance_series(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            # refracted_solar_zenith=refracted_solar_zenith,
            solar_position_model=solar_position_model,
            solar_time_model=solar_time_model,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            angle_output_units=angle_output_units,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            fingerprint=fingerprint,
        )
    )
    # solar_altitude_series = model_solar_altitude_series(
    #     longitude=longitude,
    #     latitude=latitude,
    #     timestamps=timestamps,
    #     timezone=timezone,
    #     solar_position_model=solar_position_model,
    #     apply_atmospheric_refraction=apply_atmospheric_refraction,
    #     # refracted_solar_zenith=refracted_solar_zenith,
    #     # solar_time_model=solar_time_model,
    #     perigee_offset=perigee_offset,
    #     eccentricity_correction_factor=eccentricity_correction_factor,
    #     dtype=dtype,
    #     array_backend=array_backend,
    #     verbose=verbose,  # Is this wanted here ? i.e. not setting = 0 ?
    #     log=log,
    # )
    # diffuse_horizontal_irradiance_series = (
    #     calculate_diffuse_horizontal_irradiance_series_pvgis(
    #         timestamps=timestamps,
    #         linke_turbidity_factor_series=linke_turbidity_factor_series,
    #         solar_altitude_series=solar_altitude_series,
    #         solar_constant=solar_constant,
    #         perigee_offset=perigee_offset,
    #         eccentricity_correction_factor=eccentricity_correction_factor,
    #         dtype=dtype,
    #         array_backend=array_backend,
    #         verbose=verbose,
    #         log=log,
    #         fingerprint=fingerprint,
    #     )
    # )
    global_horizontal_irradiance_series = (
        direct_horizontal_irradiance_series.value
        + diffuse_horizontal_irradiance_series.value
    )

    # Warning
    out_of_range_indices = np.where(
        (global_horizontal_irradiance_series < LOWER_PHYSICALLY_POSSIBLE_LIMIT)
        | (global_horizontal_irradiance_series > UPPER_PHYSICALLY_POSSIBLE_LIMIT)
    )
    if out_of_range_indices[0].size > 0:
        logger.warning(
            f"{WARNING_OUT_OF_RANGE_VALUES} in `global_horizontal_irradiance_series` : {out_of_range_indices[0]}!"
        )

    # Building the output dictionary ========================================

    components_container = {
        GLOBAL_HORIZONTAL_IRRADIANCE: lambda: {
            TITLE_KEY_NAME: GLOBAL_HORIZONTAL_IRRADIANCE,
            GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME: global_horizontal_irradiance_series,
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
        },  # if verbose > 0 else {},
        GLOBAL_HORIZONTAL_IRRADIANCE + " & relevant components": lambda: (
            {
                TITLE_KEY_NAME: GLOBAL_HORIZONTAL_IRRADIANCE + " & relevant components",
                DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series.value,
                DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME: diffuse_horizontal_irradiance_series.value,
            }
            if verbose > 1
            else {}
        ),
        "Irradiance Metadata": lambda: (
            {
                EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME: diffuse_horizontal_irradiance_series.components[EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME],
                ALTITUDE_COLUMN_NAME: (
                    diffuse_horizontal_irradiance_series.components[ALTITUDE_COLUMN_NAME]
                    if diffuse_horizontal_irradiance_series.components[ALTITUDE_COLUMN_NAME]
                    else None
                ),
                LINKE_TURBIDITY_COLUMN_NAME: linke_turbidity_factor_series.value,
            }
            if verbose > 2
            else {}
        ),
        "Fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(
                    global_horizontal_irradiance_series
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
        data=global_horizontal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
        value=global_horizontal_irradiance_series,
        unit=IRRADIANCE_UNIT,
        position_algorithm="",
        timing_algorithm="",
        elevation=elevation,
        surface_orientation=None,
        surface_tilt=None,
        components=components,
    )

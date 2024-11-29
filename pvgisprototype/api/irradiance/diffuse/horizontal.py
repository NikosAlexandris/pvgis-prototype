from zoneinfo import ZoneInfo

from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import Irradiance, LinkeTurbidityFactor
from pvgisprototype.algorithms.pvis.diffuse.horizontal import calculate_diffuse_horizontal_irradiance_series_pvgis
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.constants import (
    ALTITUDE_COLUMN_NAME,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DIFFUSE_HORIZONTAL_IRRADIANCE,
    DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR,
    EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_UNIT,
    LINKE_TURBIDITY_COLUMN_NAME,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    OUT_OF_RANGE_INDICES_COLUMN_NAME,
    PERIGEE_OFFSET,
    RADIANS,
    RADIATION_MODEL_COLUMN_NAME,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    TITLE_KEY_NAME,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.hashing import generate_hash


@log_function_call
def calculate_diffuse_horizontal_irradiance_series(
    longitude: float,
    latitude: float,
    timestamps: DatetimeIndex = None,
    timezone: ZoneInfo | None = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
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
):
    """ """
    # solar altitude required internally to calculate the extraterrestrial irradiance on a horizontal surface
    solar_altitude_series = model_solar_altitude_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        # refracted_solar_zenith=refracted_solar_zenith,
        # solar_time_model=solar_time_model,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,  # Is this wanted here ? i.e. not setting = 0 ?
        log=log,
    )
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

    # Building the output dictionary=========================================

    components_container = {
        "Metadata": lambda: {
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
        },
        DIFFUSE_HORIZONTAL_IRRADIANCE: lambda: {
            TITLE_KEY_NAME: DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
            DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME: diffuse_horizontal_irradiance_series,
        },
        DIFFUSE_HORIZONTAL_IRRADIANCE
        + " relevant components": lambda: (
            {
                TITLE_KEY_NAME: DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME
                + " & relevant components",
                EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME: diffuse_horizontal_irradiance_series.extraterrestrial_normal_irradiance,
                ALTITUDE_COLUMN_NAME: (
                    getattr(solar_altitude_series, angle_output_units)
                    if solar_altitude_series
                    else None
                ),
                LINKE_TURBIDITY_COLUMN_NAME: diffuse_horizontal_irradiance_series.linke_turbidity_factor,
            }
            if verbose > 2
            else {}
        ),
        "Out-of-range": lambda: (
            {
                OUT_OF_RANGE_INDICES_COLUMN_NAME: diffuse_horizontal_irradiance_series.out_of_range,
                OUT_OF_RANGE_INDICES_COLUMN_NAME + ' i': diffuse_horizontal_irradiance_series.out_of_range_index,
            }
            if diffuse_horizontal_irradiance_series.out_of_range_index[0].size > 0
            else {}
        ),
        "Fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(
                    diffuse_horizontal_irradiance_series
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
        data=diffuse_horizontal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
        value=diffuse_horizontal_irradiance_series.value,
        unit=IRRADIANCE_UNIT,
        position_algorithm=solar_position_model.value,
        timing_algorithm=solar_time_model.value,
        elevation=None,
        surface_orientation=None,
        surface_tilt=None,
        components=components,
    )

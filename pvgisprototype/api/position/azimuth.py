"""
An overview of conventions and conversions from a North-based system to either
East- or South-based systems is:

             ┌─────────────┐  ┌────────────┐  ┌────────────┐
             │     N=0     │  │     N      │  │      N     │
             │      ▲      │  │     ▲      │  │      ▲     │
     Origin  │   W ◄┼► E   │  │  W ◄┼► E=0 │  │   W ◄┼► E  │
             │      ▼      │  │     ▼      │  │      ▼     │
             │      S      │  │     S      │  │      S=0   │
             └─────────────┘  └────────────┘  └────────────┘
             ┌─────────────┐  ┌────────────┐  ┌────────────┐
             │             │  │            │  │            │
             │             │  │            │  │            │
Input South  │     180     │  │     90     │  │     0      │
    (IS)     │             │  │            │  │            │
             │             │  │            │  │            │
             └─────────────┘  └────────────┘  └────────────┘
             ┌─────────────┐  ┌────────────┐  ┌────────────┐
             │             │  │            │  │            │
   Internal  │             │  │            │  │            │
             │      =      │  │  IS - 90   │  │  IS - 180  │
  Conversion │             │  │            │  │            │
             │             │  │            │  │            │
             └─────────────┘  └────────────┘  └────────────┘

"""

from typing import Dict, List
from zoneinfo import ZoneInfo

from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import Latitude, Longitude, RefractedSolarZenith, SolarAzimuth
from pvgisprototype.algorithms.jenco.solar_azimuth import (
    calculate_solar_azimuth_series_jenco,
)
from pvgisprototype.algorithms.noaa.solar_azimuth import (
    calculate_solar_azimuth_series_noaa,
)
from pvgisprototype.algorithms.pvlib.solar_azimuth import (
    calculate_solar_azimuth_series_pvlib,
)
from pvgisprototype.api.position.models import SolarPositionModel, SolarTimeModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    AZIMUTH_NAME,
    AZIMUTH_ORIGIN_NAME,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    NOT_AVAILABLE,
    PERIGEE_OFFSET,
    POSITION_ALGORITHM_NAME,
    RADIANS,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    TIME_ALGORITHM_NAME,
    UNIT_NAME,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_function_call, logger
from pvgisprototype.validation.functions import (
    ModelSolarAzimuthTimeSeriesInputModel,
    validate_with_pydantic,
)


@log_function_call
@custom_cached
@validate_with_pydantic(ModelSolarAzimuthTimeSeriesInputModel)
def model_solar_azimuth_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex | None,
    timezone: ZoneInfo | None,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    adjust_for_atmospheric_refraction: bool = True,
    refracted_solar_zenith: RefractedSolarZenith | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    solar_time_model: SolarTimeModel = SolarTimeModel.milne,
    eccentricity_phase_offset: float = PERIGEE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    validate_output:bool = VALIDATE_OUTPUT_DEFAULT,
) -> SolarAzimuth:
    """
    The solar azimuth angle measures horizontally around the horizon from north
    through east, south, and west.

    Notes
    -----

    - All solar calculation functions return floating angular measurements in
      radians.

    pysolar :

    From https://pysolar.readthedocs.io:

    - Azimuth is reckoned with zero corresponding to north. Positive azimuth
      estimates correspond to estimates east of north; negative estimates, or
      estimates larger than 180 are west of north. In the northern hemisphere,
      if we speak in terms of (altitude, azimuth), the sun comes up around
      (0, 90), reaches (70, 180) around noon, and sets around (0, 270).

    - The result is returned with units.
    """
    logger.info(
            f"Executing solar positioning modelling function model_solar_azimuth_series() for\n{timestamps}",
            alt=f"Executing [underline]solar positioning modelling[/underline] function model_solar_azimuth_series() for\n{timestamps}"
            )
    solar_azimuth_series = None

    if solar_position_model.value == SolarPositionModel.noaa:
        solar_azimuth_series = calculate_solar_azimuth_series_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            validate_output=validate_output,
        )

    if solar_position_model.value == SolarPositionModel.jenco:
        solar_azimuth_series = calculate_solar_azimuth_series_jenco(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_position_model.value == SolarPositionModel.skyfield:
        pass
    # if solar_position_model.value == SolarPositionModel.skyfield:

    #     solar_altitude, solar_azimuth = calculate_solar_altitude_azimuth_skyfield(
    #             longitude=longitude,
    #             latitude=latitude,
    #             timestamp=timestamp,
    #             )

    if solar_position_model.value == SolarPositionModel.suncalc:
        pass
    # if solar_position_model.value == SolarPositionModel.suncalc:
    #     # note : first azimuth, then altitude
    #     solar_azimuth_south_radians_convention, solar_altitude = suncalc.get_position(
    #         date=timestamp,  # this comes first here!
    #         lng=longitude.degrees,
    #         lat=latitude.degrees,
    #     ).values()  # zero points to south
    #     solar_azimuth = convert_south_to_north_radians_convention(
    #         solar_azimuth_south_radians_convention
    #     )
    #     solar_azimuth = SolarAzimuth(
    #         value=solar_azimuth,
    #         unit=RADIANS,
    #         position_algorithm='suncalc',
    #         timing_algorithm='suncalc',
    #     )

    if solar_position_model.value == SolarPositionModel.pysolar:
        pass
        # timestamp = attach_timezone(timestamp, timezone)

        # solar_azimuth = pysolar.solar.get_azimuth(
        #     latitude_deg=longitude.degrees,  # this comes first
        #     longitude_deg=latitude.degrees,
        #     when=timestamp,
        # )  # returns degrees by default
        # # required by output function
        # solar_azimuth = SolarAzimuth(
        #     value=solar_azimuth,
        #     unit=DEGREES,
        #     position_algorithm='pysolar',
        #     timing_algorithm='pysolar',
        # )

    if solar_position_model.value == SolarPositionModel.hofierka:
        pass
        # solar_azimuth = calculate_solar_azimuth_pvis(
        #     longitude=longitude,
        #     latitude=latitude,
        #     timestamp=timestamp,
        #     timezone=timezone,
        #     solar_time_model=solar_time_model,
        # )

    if solar_position_model.value == SolarPositionModel.pvlib:
        solar_azimuth_series = calculate_solar_azimuth_series_pvlib(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    # log_data_fingerprint(
    #         data=solar_azimuth_series.value,
    #         log_level=log,
    #         hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    # )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    logger.info(
            f"Returning solar azimuth time series :\n{solar_azimuth_series}",
            alt=f"Returning [yellow]solar azimuth[/yellow] time series :\n{solar_azimuth_series}",
            )

    return solar_azimuth_series


def calculate_solar_azimuth_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    solar_position_models: List[SolarPositionModel] = [SolarPositionModel.noaa],
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    adjust_for_atmospheric_refraction: bool = True,
    refracted_solar_zenith: RefractedSolarZenith | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    eccentricity_phase_offset: float = PERIGEE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> Dict:
    """
    Calculates the solar position using all models and returns the results in a table.
    """
    results = {}
    for solar_position_model in solar_position_models:
        if (
            solar_position_model != SolarPositionModel.all
        ):  # ignore 'all' in the enumeration
            solar_azimuth_series = model_solar_azimuth_series(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                timezone=timezone,
                solar_position_model=solar_position_model,
                adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                solar_time_model=solar_time_model,
                eccentricity_phase_offset=eccentricity_phase_offset,
                eccentricity_amplitude=eccentricity_amplitude,
                verbose=verbose,
                validate_output=validate_output,
            )
            solar_azimuth_model_series = {
                solar_position_model.name: {
                    TIME_ALGORITHM_NAME: (
                        solar_azimuth_series.timing_algorithm
                        if solar_azimuth_series
                        else NOT_AVAILABLE
                    ),
                    POSITION_ALGORITHM_NAME: (
                        solar_azimuth_series.position_algorithm
                        if solar_azimuth_series
                        else NOT_AVAILABLE
                    ),
                    AZIMUTH_NAME: (
                        getattr(solar_azimuth_series, angle_output_units, NOT_AVAILABLE)
                        if solar_azimuth_series
                        else NOT_AVAILABLE
                    ),
                    AZIMUTH_ORIGIN_NAME: (
                        solar_azimuth_series.origin
                        if solar_azimuth_series
                        else NOT_AVAILABLE
                    ),
                    UNIT_NAME: angle_output_units,
                }
            }
            results = results | solar_azimuth_model_series

    return results

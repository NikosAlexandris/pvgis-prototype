from pvgisprototype.algorithms.jenco.solar_azimuth import calculate_solar_azimuth_time_series_jenco
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from typing import Optional
from typing import List
from pandas import DatetimeIndex
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.algorithms.noaa.solar_azimuth import calculate_solar_azimuth_time_series_noaa
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarAzimuthTimeSeriesInputModel
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import SolarAzimuth
from pvgisprototype import RefractedSolarZenith
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import RADIANS


@log_function_call
@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(ModelSolarAzimuthTimeSeriesInputModel)
def model_solar_azimuth_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: Optional[RefractedSolarZenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    solar_time_model: SolarTimeModel = SolarTimeModel.milne,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
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
    solar_azimuth_series = None

    if solar_position_model.value == SolarPositionModel.noaa:

        solar_azimuth_series = calculate_solar_azimuth_time_series_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_position_model.value == SolarPositionModel.jenco:

        solar_azimuth_series = calculate_solar_azimuth_time_series_jenco(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
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

    if solar_position_model.value  == SolarPositionModel.hofierka:
        pass
        # solar_azimuth = calculate_solar_azimuth_pvis(
        #     longitude=longitude,
        #     latitude=latitude,
        #     timestamp=timestamp,
        #     timezone=timezone,
        #     solar_time_model=solar_time_model,
        # )

    if solar_position_model.value  == SolarPositionModel.pvlib:
        pass
        # solar_azimuth = calculate_solar_azimuth_pvlib(
        #     longitude=longitude,
        #     latitude=latitude,
        #     timestamp=timestamp,
        #     timezone=timezone,
        # )

    log_data_fingerprint(
            data=solar_azimuth_series.value,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return solar_azimuth_series


def calculate_solar_azimuth_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    solar_position_models: List[SolarPositionModel] = [SolarPositionModel.skyfield],
    solar_time_model: SolarTimeModel = SolarTimeModel.skyfield,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: Optional[RefractedSolarZenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> List:
    """
    Calculates the solar position using all models and returns the results in a table.
    """
    results = []
    for solar_position_model in solar_position_models:
        if solar_position_model != SolarPositionModel.all:  # ignore 'all' in the enumeration
            solar_azimuth = model_solar_azimuth(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                solar_position_model=solar_position_model,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                solar_time_model=solar_time_model,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                verbose=verbose,
            )
            results.append({
                TIME_ALGORITHM_NAME: solar_azimuth.timing_algorithm,
                POSITION_ALGORITHM_NAME: solar_azimuth.position_algorithm,
                AZIMUTH_NAME if solar_azimuth else None: getattr(solar_azimuth, angle_output_units) if solar_azimuth else None,
                UNITS_NAME: angle_output_units,
            })

    return results

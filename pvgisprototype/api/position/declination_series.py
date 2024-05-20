from devtools import debug
from zoneinfo import ZoneInfo

from pandas import DatetimeIndex
from pvgisprototype import SolarDeclination
from pvgisprototype.api.position.models import SolarDeclinationModel
from pvgisprototype.api.utilities.conversions import convert_series_to_degrees_if_requested
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_time_series_noaa
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RADIANS
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from cachetools import cached
from pvgisprototype.caching import custom_hashkey


@log_function_call
@cached(cache={}, key=custom_hashkey)
def model_solar_declination_time_series(
    timestamps: DatetimeIndex,
    timezone: ZoneInfo = ZoneInfo('UTC'),
    model: SolarDeclinationModel = SolarDeclinationModel.pvis,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    verbose: int = 0,
    log: int = 0,
) -> SolarDeclination:
    """ """
    solar_declination_series = None

    if model.value == SolarDeclinationModel.noaa:

        solar_declination_series = calculate_solar_declination_time_series_noaa(
            timestamps=timestamps,
        )
        solar_declination_series = convert_series_to_degrees_if_requested(
            solar_declination_series,
            angle_output_units,
        )

    if model.value  == SolarDeclinationModel.pvis:
        pass

    if model.value  == SolarDeclinationModel.hargreaves:
        pass

    if model.value  == SolarDeclinationModel.pvlib:
        pass

    log_data_fingerprint(
        data=solar_declination_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return solar_declination_series


def calculate_solar_declination_series():
    pass

# def calculate_solar_declination(
#     timestamp: datetime,
#     timezone: ZoneInfo = None,
#     declination_models: List[SolarDeclinationModel] = [SolarDeclinationModel.pvis],
#     perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
#     eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
#     angle_output_units: str = RADIANS,
#     verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
# ) -> List:
#     """Calculate the solar declination angle

#     The solar declination is the angle between the rays of the sun and the
#     equator of the earth. It is used to calculate the solar elevation and
#     azimuth angles.
#     """
#     results = []
#     for declination_model in declination_models:
#         if declination_model != SolarDeclinationModel.all:  # ignore 'all' in the enumeration
#             solar_declination = model_solar_declination(
#                 timestamp=timestamp,
#                 timezone=timezone,
#                 declination_model=declination_model,
#                 perigee_offset=perigee_offset,
#                 eccentricity_correction_factor=eccentricity_correction_factor,
#                 verbose=verbose,
#             )
#             results.append({
#                 POSITION_ALGORITHM_NAME: declination_model.value,
#                 DECLINATION_NAME if solar_declination else None: getattr(solar_declination, angle_output_units) if solar_declination else None,
#                 UNITS_NAME: angle_output_units,
#             })

#     return results

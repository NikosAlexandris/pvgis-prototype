from devtools import debug
from typing import List, Union, Sequence
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.algorithms.noaa.solar_altitude import calculate_solar_altitude_time_series_noaa
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarAltitudeTimeSeriesInputModel
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype import SolarAltitude
from datetime import datetime
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import TIME_ALGORITHM_NAME
from pvgisprototype.constants import POSITION_ALGORITHM_NAME
from pvgisprototype.constants import ALTITUDE_NAME
from pvgisprototype.constants import UNITS_NAME


@validate_with_pydantic(ModelSolarAltitudeTimeSeriesInputModel)
def model_solar_altitude_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: Union[datetime, Sequence[datetime]],
    timezone: ZoneInfo,
    solar_position_model: SolarPositionModels = SolarPositionModels.noaa,
    apply_atmospheric_refraction: bool = True,
    verbose: int = 0,
) -> List[SolarAltitude]:

    if verbose == 3:
        debug(locals())

    if solar_position_model.value == SolarPositionModels.noaa:

        solar_altitude_series = calculate_solar_altitude_time_series_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            verbose=verbose,
        )

    if solar_position_model.value == SolarPositionModels.skyfield:
        pass

    if solar_position_model.value == SolarPositionModels.suncalc:
        pass

    if solar_position_model.value == SolarPositionModels.pysolar:
        pass

    if solar_position_model.value  == SolarPositionModels.pvis:
        pass

    if solar_position_model.value  == SolarPositionModels.pvlib:
        pass

    if verbose == 3:
        debug(locals())

    return solar_altitude_series


def calculate_solar_altitude_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: Union[datetime, Sequence[datetime]],
    timezone: ZoneInfo,
    solar_position_models: List[SolarPositionModels] = [SolarPositionModels.skyfield],
    solar_time_model: SolarTimeModels = SolarTimeModels.skyfield,
    apply_atmospheric_refraction: bool = True,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> List:
    """
    Calculates the solar position using all models and returns the results in a table.
    """
    results = []
    for solar_position_model in solar_position_models:
        if solar_position_model != SolarPositionModels.all:  # ignore 'all' in the enumeration
            solar_altitude = model_solar_altitude_time_series(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                timezone=timezone,
                solar_position_model=solar_position_model,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                verbose=verbose,
            )
            results.append({
                TIME_ALGORITHM_NAME: solar_altitude.timing_algorithm,
                POSITION_ALGORITHM_NAME: solar_position_model.value,
                ALTITUDE_NAME: getattr(solar_altitude, angle_output_units, None) if solar_altitude else None,
                UNITS_NAME: angle_output_units,
            })

    return results

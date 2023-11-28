from devtools import debug
from typing import List, Union, Sequence
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_altitude import calculate_solar_altitude_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_azimuth import calculate_solar_azimuth_time_series_noaa
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
from pvgisprototype.constants import DECLINATION_NAME
from pvgisprototype.constants import HOUR_ANGLE_NAME
from pvgisprototype.constants import POSITION_ALGORITHM_NAME
from pvgisprototype.constants import ZENITH_NAME
from pvgisprototype.constants import ALTITUDE_NAME
from pvgisprototype.constants import AZIMUTH_NAME
from pvgisprototype.constants import UNITS_NAME
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import NOT_AVAILABLE


@validate_with_pydantic(ModelSolarAltitudeTimeSeriesInputModel)
def model_solar_geometry_overview_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: Union[datetime, Sequence[datetime]],
    timezone: ZoneInfo,
    solar_position_model: SolarPositionModels = SolarPositionModels.noaa,
    apply_atmospheric_refraction: bool = True,
    solar_time_model: SolarTimeModels = SolarTimeModels.milne,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> List[SolarAltitude]:

    solar_declination_series = None  # updated if applicable
    solar_hour_angle_series = None
    solar_zenith_series = None  # updated if applicable
    solar_altitude_series = None
    solar_azimuth_series = None

    if verbose > 6:
        debug(locals())

    if solar_position_model.value == SolarPositionModels.noaa:

        solar_declination_series = calculate_solar_declination_time_series_noaa(
            timestamps=timestamps,
        )
        solar_hour_angle_series = calculate_solar_hour_angle_time_series_noaa(
            longitude=longitude,
            timestamps=timestamps,
            timezone=timezone,
            verbose=verbose,
        )
        solar_zenith_series = calculate_solar_zenith_time_series_noaa(
            latitude=latitude,
            timestamps=timestamps,
            solar_hour_angle_series=solar_hour_angle_series,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            verbose=verbose,
        )
        solar_altitude_series = calculate_solar_altitude_time_series_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            verbose=verbose,
        )
        solar_azimuth_series = calculate_solar_azimuth_time_series_noaa(
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

    if solar_position_model.value == SolarPositionModels.pvis:
        pass

    if solar_position_model.value == SolarPositionModels.pvlib:
        pass

    position_series = (
        solar_declination_series if solar_declination_series is not None else None,
        solar_hour_angle_series if solar_hour_angle_series is not None else None,
        solar_zenith_series if solar_zenith_series is not None else None,
        solar_altitude_series if solar_altitude_series is not None else None,
        solar_azimuth_series if solar_azimuth_series is not None else None,
    )
    if verbose > 6:
        debug(locals())

    return position_series


def calculate_solar_geometry_overview_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: datetime,
    timezone: ZoneInfo,
    solar_position_models: List[SolarPositionModels] = [SolarPositionModels.skyfield],
    solar_time_model: SolarTimeModels = SolarTimeModels.skyfield,
    apply_atmospheric_refraction: bool = True,
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
        if solar_position_model != SolarPositionModels.all:  # ignore 'all' in the enumeration
            (
                solar_declination_series,
                solar_hour_angle_series,
                solar_zenith_series,
                solar_altitude_series,
                solar_azimuth_series,
            ) = model_solar_geometry_overview_time_series(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                timezone=timezone,
                solar_position_model=solar_position_model,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                solar_time_model=solar_time_model,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                verbose=verbose,
            )
            results.append({
                TIME_ALGORITHM_NAME: solar_azimuth_series.timing_algorithm if solar_azimuth_series else NOT_AVAILABLE,
                DECLINATION_NAME: getattr(solar_declination_series, angle_output_units, NOT_AVAILABLE) if solar_declination_series else NOT_AVAILABLE,
                HOUR_ANGLE_NAME: getattr(solar_hour_angle_series, angle_output_units, NOT_AVAILABLE) if solar_hour_angle_series else NOT_AVAILABLE,
                POSITION_ALGORITHM_NAME: solar_position_model.value,
                ZENITH_NAME: getattr(solar_zenith_series, angle_output_units, NOT_AVAILABLE) if solar_zenith_series else NOT_AVAILABLE,
                ALTITUDE_NAME: getattr(solar_altitude_series, angle_output_units, NOT_AVAILABLE) if solar_altitude_series else NOT_AVAILABLE,
                AZIMUTH_NAME: getattr(solar_azimuth_series, angle_output_units, NOT_AVAILABLE) if solar_azimuth_series else NOT_AVAILABLE,
                UNITS_NAME: angle_output_units,
            })

    return results

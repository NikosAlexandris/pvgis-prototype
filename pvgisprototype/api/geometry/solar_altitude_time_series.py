from devtools import debug
from typing import List, Union, Sequence
from datetime import datetime
from pvgisprototype.algorithms.noaa.solar_altitude import calculate_solar_altitude_time_series_noaa
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarAltitudeTimeSeriesInputModel
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype import SolarAltitude
from datetime import datetime


@validate_with_pydantic(ModelSolarAltitudeTimeSeriesInputModel)
def model_solar_altitude_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: Union[datetime, Sequence[datetime]],
    timezone: str,
    solar_position_model: SolarPositionModels,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: float = 1.5853349194640094,
    solar_time_model: SolarTimeModels = SolarTimeModels.skyfield,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    days_in_a_year: float = 365.25,
    perigee_offset: float = 0.048869,
    eccentricity_correction_factor: float = 0.01672,
    time_output_units: str = 'minutes',
    angle_output_units: str = 'radians',
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
            # time_output_units=time_output_units,
            # angle_output_units=angle_output_units,
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

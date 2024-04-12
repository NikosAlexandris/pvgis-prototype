from devtools import debug
from typing import Union
from typing import Sequence
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarTimeTimeSeriesInputModel
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from .models import SolarTimeModel
from pvgisprototype.algorithms.noaa.solar_time import calculate_true_solar_time_time_series_noaa
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RADIANS


@validate_with_pydantic(ModelSolarTimeTimeSeriesInputModel)
def model_solar_time_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: Union[datetime, Sequence[datetime]],
    timezone: ZoneInfo = None,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: float = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_offset_global: float = 0,  # for `pvgis`
    hour_offset: float = 0,  # for `pvgis`
    time_output_units: str = "minutes",
    angle_units: str = RADIANS,
    verbose: int = 0,
):
    """Calculates the solar time using the requested _algorithm_.

    Parameters
    ----------
    input : SolarTimeInput

    Returns
    -------
    SolarTime
    """
    # if local and timestamp is not None and timezone is not None:
    #     timestamp = timezone.localize(timestamp)
    if solar_time_model.value == SolarTimeModel.milne:

        pass

    if solar_time_model.value == SolarTimeModel.ephem:

        pass

    if solar_time_model.value == SolarTimeModel.pvgis:

        # Requires : time_offset_global, hour_offset

        pass

    if solar_time_model.value == SolarTimeModel.noaa:

        solar_time_series = calculate_true_solar_time_time_series_noaa(
            longitude=longitude,
            # latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            # refracted_solar_zenith=refracted_solar_zenith,
            # apply_atmospheric_refraction=apply_atmospheric_refraction,
            time_output_units=time_output_units,
            angle_units=angle_units,
            # angle_output_units=angle_output_units,
            verbose=verbose,
        )

    if solar_time_model.value == SolarTimeModel.skyfield:

        pass

    return solar_time_series

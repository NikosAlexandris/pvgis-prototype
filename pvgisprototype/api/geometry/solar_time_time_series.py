from devtools import debug
from typing import Union
from typing import Sequence
# from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarTimeTimeSeriesInputModel
# from pvgisprototype import SolarTime
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from .models import SolarTimeModels
# from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
# from pvgisprototype.algorithms.milne1921.solar_time import calculate_apparent_solar_time_milne1921
# from pvgisprototype.algorithms.pyephem.solar_time import calculate_solar_time_ephem
# from pvgisprototype.algorithms.pvgis.solar_time import calculate_solar_time_pvgis
from pvgisprototype.algorithms.noaa.solar_time import calculate_true_solar_time_time_series_noaa
# from pvgisprototype.algorithms.skyfield.solar_time import calculate_solar_time_skyfield
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import DAYS_IN_A_YEAR
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
# from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT


@validate_with_pydantic(ModelSolarTimeTimeSeriesInputModel)
def model_solar_time_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: Union[datetime, Sequence[datetime]],
    timezone: ZoneInfo = None,
    solar_time_model: SolarTimeModels = SolarTimeModels.skyfield,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: float = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    days_in_a_year: float = DAYS_IN_A_YEAR,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    time_output_units: str = "minutes",
    angle_units: str = "radians",
    angle_output_units: str = "radians",
    verbose: int = 0,
):
    """Calculates the solar time and returns the calculated value and the units.

    Parameters
    ----------
    input : SolarTimeInput

    Returns
    -------
    SolarTime
    """
    # if local and timestamp is not None and timezone is not None:
    #     timestamp = timezone.localize(timestamp)
    if solar_time_model.value == SolarTimeModels.milne:

        pass

    if solar_time_model.value == SolarTimeModels.ephem:

        pass

    if solar_time_model.value == SolarTimeModels.pvgis:

        pass

    if solar_time_model.value == SolarTimeModels.noaa:

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

    if solar_time_model.value == SolarTimeModels.skyfield:

        pass

    return solar_time_series

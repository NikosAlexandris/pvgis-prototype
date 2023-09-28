from devtools import debug
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo

from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarTimeInputModel
from pvgisprototype import SolarTime
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from .models import SolarTimeModels
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.algorithms.milne1921.solar_time import calculate_apparent_solar_time_milne1921
from pvgisprototype.algorithms.pyephem.solar_time import calculate_solar_time_ephem
from pvgisprototype.algorithms.pvgis.solar_time import calculate_solar_time_pvgis
from pvgisprototype.algorithms.noaa.solar_time import calculate_true_solar_time_noaa
# from pvgisprototype.algorithms.noaa.solar_position import calculate_local_solar_time_noaa
from pvgisprototype.algorithms.skyfield.solar_time import calculate_solar_time_skyfield
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import DAYS_IN_A_YEAR
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT

@validate_with_pydantic(ModelSolarTimeInputModel)
def model_solar_time(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
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

        solar_time = calculate_apparent_solar_time_milne1921(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            days_in_a_year=days_in_a_year,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_offset_global=time_offset_global,
            hour_offset=hour_offset,
            verbose=verbose,
        )

    if solar_time_model.value == SolarTimeModels.ephem:

        solar_time = calculate_solar_time_ephem(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            verbose=verbose,
        )

    if solar_time_model.value == SolarTimeModels.pvgis:

        solar_time = calculate_solar_time_pvgis(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            time_offset_global=time_offset_global,
            verbose=verbose,
        )

    if solar_time_model.value == SolarTimeModels.noaa:

        solar_time = calculate_true_solar_time_noaa(
            longitude=longitude,
            # latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            # refracted_solar_zenith=refracted_solar_zenith,
            # apply_atmospheric_refraction=apply_atmospheric_refraction,
            time_output_units=time_output_units,
            angle_units=angle_units,
            # angle_output_units=angle_output_units,
            verbose=verbose,
        )
        # solar_time = calculate_local_solar_time_noaa(
        #     longitude=longitude,
        #     latitude=latitude,
        #     timestamp=timestamp,
        #     timezone=timezone,
        #     refracted_solar_zenith=refracted_solar_zenith,
        #     apply_atmospheric_refraction=apply_atmospheric_refraction,
        #     time_output_units=time_output_units,
        #     angle_units=angle_units,
        #     angle_output_units=angle_output_units,
        #     # verbose,
        # )

    if solar_time_model.value == SolarTimeModels.skyfield:

        longitude = convert_to_degrees_if_requested(longitude, 'degrees')
        latitude = convert_to_degrees_if_requested(latitude, 'degrees')
        # vvv vvv vvv --------------------------------------- expects degrees!
        solar_time = calculate_solar_time_skyfield(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            verbose=verbose,
        )
        # ^^^ ^^^ ^^^ --------------------------------------- expects degrees!

    return solar_time


def calculate_solar_time(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: str = None,
    models: List[SolarTimeModels] = [SolarTimeModels.skyfield],
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: float = 1.5853349194640094,  # radians
    days_in_a_year: float = 365.25,
    perigee_offset: float = 0.048869,
    eccentricity_correction_factor: float = 0.03344,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    time_output_units: str = "minutes",
    angle_units: str = "radians",
    angle_output_units: str = "radians",
    verbose: int = 0,
) -> List:
    """Calculates the solar time using all models and returns the results in a table.

    Parameters
    ----------
    
    Returns
    -------

    """
    results = []
    for model in models:
        if model != SolarTimeModels.all:  # ignore 'all' in the enumeration
            solar_time = model_solar_time(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                solar_time_model=model,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                days_in_a_year=days_in_a_year,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                time_offset_global=time_offset_global,
                hour_offset=hour_offset,
                time_output_units=time_output_units,
                angle_output_units=angle_output_units,
                verbose=verbose,
            )
            results.append({
                'Model': model,
                'Solar time': solar_time,
                # 'Units': solar_time,  # Don't trust me -- Redesign Me!
            })

    return results

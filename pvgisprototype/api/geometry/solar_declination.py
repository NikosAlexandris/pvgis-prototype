from devtools import debug
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from math import pi
from math import sin
from math import asin

from pvgisprototype.api.decorators import validate_with_pydantic
from pvgisprototype.api.function_models import CalculateFractionalYearPVISInputModel
from pvgisprototype.api.models import FractionalYear
from pvgisprototype.api.function_models import CalculateSolarDeclinationPVISInputModel
from pvgisprototype.api.models import SolarDeclination
from .models import SolarDeclinationModels
from ..utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.algorithms.pvis.solar_declination import calculate_solar_declination_pvis
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_noaa
from pvgisprototype.algorithms.hargreaves.solar_declination import calculate_solar_declination_hargreaves


def model_solar_declination(
    timestamp: datetime,
    timezone: ZoneInfo = None,
    model: SolarDeclinationModels = SolarDeclinationModels.pvis,
    days_in_a_year: float = 365.25,
    perigee_offset: float = 0.048869,
    eccentricity_correction_factor: float = 0.01672,
    angle_output_units: str = 'radians',
) -> SolarDeclination:
    """ """
    if model.value == SolarDeclinationModels.noaa:

        solar_declination = calculate_solar_declination_noaa(
            timestamp=timestamp,
            angle_output_units=angle_output_units
        )
        solar_declination = convert_to_degrees_if_requested(
            solar_declination,
            angle_output_units,
        )

    if model.value  == SolarDeclinationModels.pvis:

        solar_declination = calculate_solar_declination_pvis(
            timestamp=timestamp,
            timezone=timezone,
            days_in_a_year=days_in_a_year,
            eccentricity_correction_factor=eccentricity_correction_factor,
            perigee_offset=perigee_offset,
            angle_output_units=angle_output_units,
        )
        solar_declination = convert_to_degrees_if_requested(
            solar_declination,
            angle_output_units,
        )

    if model.value  == SolarDeclinationModels.hargreaves:

        solar_declination = calculate_solar_declination_hargreaves(
            timestamp=timestamp,
            days_in_a_year=days_in_a_year,
            angle_output_units=angle_output_units,
        ) # returns values in degrees by default

    return solar_declination


def calculate_solar_declination(
    timestamp: datetime,
    timezone: ZoneInfo = None,
    local_time: bool = False,
    random_time: bool = False,
    models: List[SolarDeclinationModels] = [SolarDeclinationModels.pvis],
    days_in_a_year: float = 365.25,
    perigee_offset: float = 0.048869,
    eccentricity_correction_factor: float = 0.01672,
    angle_output_units: str = 'radians',
) -> List:
    """Calculate the solar declination angle"""
    results = []
    for model in models:
        if model != SolarDeclinationModels.all:  # ignore 'all' in the enumeration
            solar_declination = model_solar_declination(
                timestamp=timestamp,
                timezone=timezone,
                model=model,
                days_in_a_year=days_in_a_year,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                angle_output_units=angle_output_units,
            )
            results.append({
                'Model': model.value,
                'Declination': solar_declination.value,
                'Units': solar_declination.unit,  # Don't trust me -- Redesign Me!
            })

    return results

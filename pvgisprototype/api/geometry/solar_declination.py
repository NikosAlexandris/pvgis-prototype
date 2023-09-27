from devtools import debug
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from math import pi
from math import sin
from math import asin

from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateFractionalYearPVISInputModel
from pvgisprototype.validation.functions import CalculateSolarDeclinationPVISInputModel
from pvgisprototype import FractionalYear
from pvgisprototype import SolarDeclination
from .models import SolarDeclinationModels
from ..utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.algorithms.pvis.solar_declination import calculate_solar_declination_pvis
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_noaa
from pvgisprototype.algorithms.hargreaves.solar_declination import calculate_solar_declination_hargreaves
from pvgisprototype.algorithms.pvlib.solar_declination import calculate_solar_declination_pvlib
from pvgisprototype.cli.typer_parameters import typer_option_days_in_a_year
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.constants import DAYS_IN_A_YEAR
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT


def model_solar_declination(
    timestamp: datetime,
    timezone: ZoneInfo = None,
    model: SolarDeclinationModels = SolarDeclinationModels.pvis,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = DAYS_IN_A_YEAR,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = 'radians',
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
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

    if model.value  == SolarDeclinationModels.pvlib:

        solar_declination = calculate_solar_declination_pvlib(
            timestamp=timestamp,
            angle_output_units=angle_output_units,
        )
        solar_declination = convert_to_degrees_if_requested(
            solar_declination,
            angle_output_units,
        )

    return solar_declination


def calculate_solar_declination(
    timestamp: datetime,
    timezone: ZoneInfo = None,
    local_time: bool = False,
    random_time: bool = False,
    models: List[SolarDeclinationModels] = [SolarDeclinationModels.pvis],
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = DAYS_IN_A_YEAR,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = 'radians',
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
) -> List:
    """Calculate the solar declination angle

    The solar declination is the angle between the rays of the sun and the
    equator of the earth. It is used to calculate the solar elevation and
    azimuth angles.
    """
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

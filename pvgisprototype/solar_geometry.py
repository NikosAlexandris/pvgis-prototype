import logging
from pvgisprototype.data_structures import SolarGeometryDayConstants
from pvgisprototype.data_structures import SolarGeometryDayVariables
import typer
from typing import Annotated


def calculate_solar_geometry_constants(
        latitude: Annotated[float, typer.Argument(
            help='Latitude in decimal degrees, south is negative',
            min=-90, max=90)],
        local_solar_time: float,
        cosine_of_declination: float,
        sine_of_declination: float,
        time_offset: float = 0,
        EPS: float = 1e-5,
) -> SolarGeometryDayConstants:
    """
    Compute solar geometry constants for the day.

    Parameters
    ----------
    local_solar_time : float
        Longitude time.
    cosine_of_declination : float
        Cosine of the solar declination.
    sine_of_declination : float
        Sine of the solar declination.

    Returns
    -------
    SolarGeometryDayConstants
        Solar geometry constants for the day.
    """
    solar_geometry_constants = calculate_solar_geometry_constants(
            latitude,
            local_solar_time,
            cosine_of_declination,
            sine_of_declination,
            )
    typer.echo(solar_geometry_constants)
    return solar_geometry_constants


def calculate_solar_geometry_variables(
        solar_geometry_day_constants: SolarGeometryDayConstants,
        year: int,
        hour_of_year: int,
        days_in_a_year: float = 365.25,
        perigee_offset = 0.048869,
        eccentricity = 0.01672,
        hour_offset: float = 0,
        output_units: Annotated[str, typer.Option(
            '-o',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ) -> SolarGeometryDayVariables:
    """Compute solar geometry variables for a given year and hour of year

    Parameters
    ----------
    solar_geometry_day_constants : SolarGeometryDayConstants
        The input solar geometry constants.
    """
    solar_geometry_constants = calculate_solar_geometry_constants(
            latitude,
            local_solar_time,
            cosine_of_declination,
            sine_of_declination,
            )
    solar_geometry_variables = calculate_solar_geometry_variables(
            solar_geometry_day_constants,
            year,
            hour_of_year,
            )

    typer.echo(solar_geometry_variables)
    return solar_geometry_variables

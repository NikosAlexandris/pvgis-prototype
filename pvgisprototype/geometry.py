"""
Important sun and solar surface geometry parameters in calculating the amount of solar radiation that reaches a particular location on the Earth's surface
"""

import typer
from typing import Annotated
from typing import Optional
from typing import Union
from typing import List
from rich.console import Console
from rich.table import Table
from datetime import datetime
import math
import numpy as np
from tzlocal import get_localzone

from .timestamp import now_datetime
from .timestamp import ctx_convert_to_timezone
from .timestamp import attach_timezone
from .timestamp import convert_hours_to_seconds
from .conversions import convert_to_radians
from .conversions import convert_to_degrees_if_requested

from .solar_declination import calculate_solar_declination
from .solar_incidence import calculate_solar_incidence
from .solar_time import calculate_solar_time_ephem
from .solar_time import calculate_hour_angle
from .solar_time import calculate_hour_angle_sunrise
from .solar_altitude import calculate_solar_altitude
from .solar_azimuth import calculate_solar_azimuth
from .solar_position import SolarPositionModels
from .solar_position import calculate_solar_position


console = Console()
app = typer.Typer(
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":triangular_ruler:  Calculate solar geometry parameters for a location and moment in time",
)


def convert_dictionary_to_table(dictionary):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Key", style="dim", width=12)
    table.add_column("Value")

    for key, value in dictionary.items():
        table.add_row(str(key), str(value))
    
    return table


def _parse_models(value: List[SolarPositionModels]) -> List[SolarPositionModels]:
    if SolarPositionModels.all in value:
        # Return all models except 'all' itself
        return [model for model in SolarPositionModels if model != SolarPositionModels.all]
    else:
        return value


@app.command('position', no_args_is_help=True, help='Calculate solar position parameters (altitude, azimuth)')
def position(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        model: Annotated[List[SolarPositionModels], typer.Option(
            '-m',
            '--model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            help="Model(s) to calculate solar position. Add multiple models like: --model Skyfield --model PVGIS")] = [SolarPositionModels.skyfield],
        output_units: Annotated[str, typer.Option(
            '-u',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar declination (degrees or radians)")] = 'radians',
        ):
    """
    """
    if SolarPositionModels.all in model:
        models = [model for model in SolarPositionModels if model != SolarPositionModels.all]

    solar_position = calculate_solar_position(
            longitude,
            latitude,
            timestamp,
            timezone,
            models,
            output_units,
            )
    solar_position_table = Table("Model", "Altitude", "Azimuth")
    for model_result in solar_position:
        model_name = model_result.get('Model', '')
        altitude = model_result.get('Altitude', '')
        azimuth = model_result.get('Azimuth', '')
        # units = model_result.get('Units', '')
        solar_position_table.add_row(model_name, str(altitude), str(azimuth))

    console.print(solar_position_table)


@app.command('altitude', no_args_is_help=True, help='Calculate the solar altitude')
def altitude(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        latitude: Annotated[Optional[float], typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ) -> float:
    """Compute various solar geometry variables.

    The solar altitude angle (SAA) is the complement of the solar zenith angle,
    measuring from the horizon directly below the sun to the sun itself. An
    altitude of 0 degrees means the sun is on the horizon, and an altitude of
    90 degrees means the sun is directly overhead.

    Parameters
    ----------
    solar_geometry_day_constants : SolarGeometryDayConstants
        The input solar geometry constants.
    """
    solar_altitude = calculate_solar_altitude(
            longitude,
            latitude,
            timestamp,
            timezone,
            output_units,
            )
    if output_units == 'degrees':
        output_units += ' °'
    typer.echo(f'Solar altitude: {solar_altitude} ({output_units})')
    return solar_altitude


@app.command('zenith', no_args_is_help=True, help='Calculate the solar zenith')
def zenith(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        latitude: Annotated[Optional[float], typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ) -> float:
    """Calculate the solar zenith angle

    The solar zenith angle (SZA) is the angle between the zenith (directly
    overhead) and the line to the sun. A zenith angle of 0 degrees means the
    sun is directly overhead, while an angle of 90 degrees means the sun is on
    the horizon.

    Parameters
    ----------
    solar_geometry_day_constants : SolarGeometryDayConstants
        The input solar geometry constants.
    """
    solar_altitude = calculate_solar_altitude(
            longitude,
            latitude,
            timestamp,
            timezone,
            output_units,
            )
    solar_zenith = 90 - solar_altitude
    typer.echo(f'Solar zenith: {solar_zenith} ({output_units})')
    return solar_zenith


@app.command('azimuth', no_args_is_help=True, help='Calculate the solar azimuth')
def azimuth(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        latitude: Annotated[Optional[float], typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        days_in_a_year: float = 365.25,
        perigee_offset: float = 0.048869,
        eccentricity: float = 0.01672,
        hour_offset: float = 0,
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ) -> float:
    """Calculate the solar azimuth angle

    The solar azimuth angle (Az) specifies the east-west orientation of the
    sun. It is usually measured from the south, going positive to the west. The
    exact definitions can vary, with some sources defining the azimuth with
    respect to the north, so care must be taken to use the appropriate
    convention.

    Parameters
    ----------

    Returns
    -------
    solar_azimuth: float
    """
    solar_azimuth = calculate_solar_azimuth(
        longitude,
        latitude,
        timestamp,
        timezone,
        days_in_a_year,
        perigee_offset,
        eccentricity,
        hour_offset,
        output_units,
        )
    typer.echo(f'Solar azimuth: {solar_azimuth} ({output_units})')
    return solar_azimuth


@app.command('declination', no_args_is_help=True, help='Calculate the solar declination')
def declination(
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        local: Annotated[bool, typer.Option(
            help='Use the system\'s local time zone',
            callback=get_localzone)] = False,
        # timezone_str: str = typer.Option(None, help="The string representing the timezone"),
        #        local: bool = typer.Option(False, help="Use the local timezone")):
        days_in_a_year: float = 365.25,
        orbital_eccentricity: float = 0.03344,
        perigee_offset: float = 0.048869,
        output_units: Annotated[str, typer.Option(
            '-o',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar declination (degrees or radians)")] = 'radians',
        ) -> float:
    """Calculat the solar declination angle 

    The solar declination (delta) is the angle between the line from the Earth
    to the Sun and the plane of the Earth's equator. It varies between ±23.45
    degrees over the course of a year as the Earth orbits the Sun.

    Parameters
    ----------

    Returns
    -------
    solar_declination: float
    """
    solar_declination = calculate_solar_decliation(
        timestamp,
        timezone,
        local,
        days_in_a_year,
        orbital_eccentricity,
        perigee_offset,
        output_units,
        )

    typer.echo(f'Solar declination: {solar_declination} ({output_units})')
    return solar_declination


@app.command('surface-orientation', no_args_is_help=True, help='Calculate the solar surface orientation (azimuth)')
def surface_orientation():
    """Calculate the surface azimuth angle

    The surface azimuth or orientation (also known as Psi) is the angle between
    the projection on a horizontal plane of the normal to a surface and the
    local meridian, with north through east directions being positive.
    """
    pass


@app.command('surface-tilt', no_args_is_help=True, help='Calculate the solar surface tile (slope)')
def surface_tilt():
    """Calculate the surface tilt angle

    The surface tilt (or slope, also known as beta) is the angle between the
    plane of the surface and the horizontal plane. A horizontal surface has a
    slope of 0°, and a vertical surface has a slope of 90°.
    """
    pass


@app.command('incidence', no_args_is_help=True, help='Calculate the solar incidence_angle')
def incidence(
        latitude: Annotated[Optional[float], typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        solar_declination: Annotated[Optional[float], typer.Argument(
            min=0, max=90)] = 0,
        surface_tilt: Annotated[Optional[float], typer.Argument(
            min=0, max=90)] = 0,
        surface_orientation: Annotated[Optional[float], typer.Argument(
            min=0, max=360)] = 180,
        hour_angle: Annotated[Optional[float], typer.Argument(
            min=0, max=1)] = None,
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ):
    """Calculate the angle of incidence

    The angle of incidence (also known as theta) is the angle between the
    direct beam of sunlight and the line perpendicular (normal) to the surface.
    If the sun is directly overhead and the surface is flat (horizontal), the
    angle of incidence is 0°.
    """
    pass


@app.command('hour-angle', no_args_is_help=True, help='Calculate the hour angle (ω)')
def hour_angle(
        solar_time: Annotated[float, typer.Argument(
            help='The solar time in decimal hours on a 24 hour base',
            callback=convert_hours_to_seconds)],
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ):
    """Calculate the hour angle 'ω = (ST / 3600 - 12) * 15 * 0.0175'

    The hour angle (ω) is the angle at any instant through which the earth has
    to turn to bring the meridian of the observer directly in line with the
    sun's rays measured in radian. In other words, it is a measure of time,
    expressed in angular measurement, usually degrees, from solar noon. It
    increases by 15° per hour, negative before solar noon and positive after
    solar noon.
    """
    hour_angle = calculate_hour_angle(
            solar_time=solar_time,
            output_units=output_units,
            )
    # typer.echo(f'Solar time: {hour_angle} ({timezone})')
    typer.echo(f'Solar time: {hour_angle} ({output_units})')


@app.command('sunrise', no_args_is_help=True, help='Calculate the hour angle (ω) at sun rise and set')
def hour_angle(
        latitude: Annotated[Optional[float], typer.Argument(
            min=-90, max=90)],
        surface_tilt: Annotated[Optional[float], typer.Argument(
            min=0, max=90)] = 0,
        solar_declination: Annotated[Optional[float], typer.Argument(
            min=-90, max=90)] = 180,
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ):
    """Calculate the hour angle 'ω = (ST / 3600 - 12) * 15 * 0.0175'

    The hour angle (ω) is the angle at any instant through which the earth has
    to turn to bring the meridian of the observer directly in line with the
    sun's rays measured in radian. In other words, it is a measure of time,
    expressed in angular measurement, usually degrees, from solar noon. It
    increases by 15° per hour, negative before solar noon and positive after
    solar noon.
    """
    hour_angle = calculate_hour_angle_sunrise(
            latitude,
            surface_tilt,
            solar_declination,
            output_units=output_units,
            )
    typer.echo(f'Solar time: {hour_angle} ({output_units})')

if __name__ == "__main__":
    app()

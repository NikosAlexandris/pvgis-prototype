import logging
from pvgisprototype.data_structures import SolarGeometryDayConstants
from pvgisprototype.data_structures import SolarGeometryDayVariables
import typer
from typing import Annotated
def get_day_from_hour_of_year(year: int, hour_of_year: int):
    """Get day of year from hour of year."""
    start_of_year = np.datetime64(f'{year}-01-01')
    date_and_time = start_of_year + np.timedelta64(hour_of_year, 'h')
    date_and_time = date_and_time.astype(datetime.datetime)
    day_of_year = int(date_and_time.strftime('%j'))
    # month = int(date_and_time.strftime('%m'))  # Month
    # day_of_month = int(date_and_time.strftime('%d'))
    # hour_of_day = int(date_and_time.strftime('%H'))

    return day_of_year


def convert_to_degrees_if_requested(angle: float, output_units: str) -> float:
    """Convert angle from radians to degrees if requested."""

    return np.degrees(angle) if output_units == 'degrees' else angle


@app.callback(invoke_without_command=True)
def calculate_solar_time(
        year: int,
        hour_of_year: int,
        days_in_a_year: float = 365.25,
        perigee_offset = 0.048869,
        eccentricity = 0.01672,
        hour_offset: float = 0,
):
    """Calculate the solar time.

    1. Map the day of the year onto the circumference of a circle, essentially
    converting the day of the year into radians.

    2. Approximate empirically the equation of time, which accounts for the
    elliptical shape of Earth's orbit and the tilt of its axis.

    3. Calculate the solar time by adding the current hour of the year, the
    time offset from the equation of time, and the hour offset (likely a
    longitude-based correction).
    """
    day_of_year = get_day_from_hour_of_year(year, hour_of_year)
    day_of_year_in_radians = double_numpi * day_of_year / days_in_a_year  
    time_offset = -0.128 * np.sin(day_of_year_in_radians - perigee_offset) - eccentricity * np.sin(2 * day_of_year_in_radians + 0.34383)
    solar_time = hour_of_year % 24 + time_offset + hour_offset

    return solar_time


@app.callback(invoke_without_command=True)
def calculate_solar_altitude(
        # solar_geometry_day_constants: SolarGeometryDayConstants,
        latitude: Annotated[Optional[float], typer.Argument(min=-90, max=90)],
        year: int,
        day_of_year: float,
        hour_of_year: int,
        output_units: Annotated[str, typer.Option(
            '-o',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ) -> SolarGeometryDayVariables:
    """Compute various solar geometry variables.

    Parameters
    ----------
    solar_geometry_day_constants : SolarGeometryDayConstants
        The input solar geometry constants.
    """
    solar_declination = calculate_solar_declination(day_of_year)
    C31 = math.cos(latitude) * math.cos(solar_declination)
    C33 = math.sin(latitude) * math.sin(solar_declination)
    solar_time = calculate_solar_time(year, hour_of_year)
    hour_angle = 0.261799 * (solar_time - 12)
    sine_solar_altitude = C31 * math.cos(hour_angle) + C33
    solar_altitude = convert_to_degrees_if_requested(
            np.arcsin(sine_solar_altitude),
            output_units
            )
    return solar_altitude


# Clean-Up --------------------------------------------------------------------
@app.callback(invoke_without_command=True)
def calculate_solar_azimuth(
        latitude: Annotated[Optional[float], typer.Argument(min=-90, max=90)],
        year: int,
        day_of_year: float,
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
    """Compute various solar geometry variables.

    Parameters
    ----------

    Returns
    -------
    solar_azimuth: float

    """
    solar_declination = calculate_solar_declination(day_of_year)
    C11 = math.sin(latitude) * math.cos(solar_declination)
    C13 = -math.cos(latitude) * math.sin(solar_declination)
    C22 = math.cos(solar_declination)
    C31 = math.cos(latitude) * math.cos(solar_declination)
    C33 = math.sin(latitude) * math.sin(solar_declination)
    solar_time = calculate_solar_time(year, hour_of_year)
    hour_angle = np.radians(15) * (solar_time - 12)
    cosine_solar_azimuth = (C11 * math.cos(hour_angle + C13)) / pow(
    pow((C22 * math.sin(hour_angle)), 2) + pow((C11 * math.cos(hour_angle) + C13), 2), 0.5
)
    solar_azimuth = math.acos(cosine_solar_azimuth)
    solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, output_units)

    return solar_azimuth


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

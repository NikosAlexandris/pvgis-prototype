import typer
from typing import Annotated
from enum import Enum
from datetime import datetime
from datetime import timezone
import suncalc
import pysolar
from pvgisprototype.solar_geometry_variables import calculate_solar_altitude
from pvgisprototype.solar_geometry_variables import calculate_solar_azimuth
from pvgisprototype.conversions import convert_to_degrees_if_requested
from pvgisprototype.conversions import convert_to_radians_if_requested

from rich.console import Console
from rich.table import Table

console = Console()

class SolarPositionModels(str, Enum):
    suncalc = 'suncalc'
    pysolar = 'pysolar'
    pvgis_new = 'pvgis-new'


# def select_solar_position_model(
#         longitude: float,
#         latitude: float,
#         timestamp: datetime,
#         model: str,
# ):
#     """Select solar position model"""
#     if model == 'suncalc':
#         solar_azimuth, solar_altitude = suncalc.get_position(
#                 timestamp,  # this comes first here!
#                 longitude,
#                 latitude,
#                 )
#     if model == 'pysolar':
#         solar_altitude = pysolar.solar.get_altitude(
#                 latitude,  # this comes first
#                 longitude,
#                 when=timestamp,
#                 )
#         solar_azimuth = pysolar.solar.get_azimuth(
#                 latitude,  # this comes first
#                 longitude,
#                 when=timestamp,
#                 )
#     return solar_altitude, solar_azimuth


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Calculate the solar altitude and azimuth for a day in the year",
)


@app.callback(invoke_without_command=True, no_args_is_help=True)
def calculate_solar_position(
        longitude: float,
        latitude: float,
        timestamp: datetime,
        model: Annotated[SolarPositionModels, typer.Option(
            '-m',
            '--model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            help="Model to calculate solar position")] = 'suncalc',
        output_units: Annotated[str, typer.Option(
            '-u',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar declination (degrees or radians)")] = 'degrees',
        ):
    """
    """
    # cleaner implementation? ------------------------------------
    # solar_azimuth, solar_altitude = select_solar_position_model(
    #         longitude,
    #         latitude,
    #         datetime,
    #         model)

    timestamp = timestamp.replace(tzinfo=timezone.utc)
    if model.value == 'suncalc':
        # note : first azimuth, then altitude
        solar_azimuth, solar_altitude = suncalc.get_position(
                date=timestamp,  # this comes first here!
                lng=longitude,
                lat=latitude,
                ).values()
        solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, output_units)
        solar_altitude = convert_to_degrees_if_requested(solar_altitude, output_units)
    
    if model.value  == 'pysolar':

        solar_altitude = pysolar.solar.get_altitude(
                latitude_deg=longitude,  # this comes first
                longitude_deg=latitude,
                when=timestamp,
                )
        solar_altitude = convert_to_radians_if_requested(solar_altitude, output_units)

        solar_azimuth = pysolar.solar.get_azimuth(
                latitude_deg=longitude,  # this comes first
                longitude_deg=latitude,
                when=timestamp,
                )
        solar_azimuth = convert_to_radians_if_requested(solar_azimuth, output_units)

    if model.value  == 'pvgis-new':

        year = timestamp.year
        start_of_year = datetime(year=year, month=1, day=1, tzinfo=timezone.utc)
        day_of_year = timestamp.timetuple().tm_yday
        hour_of_year = int((timestamp - start_of_year).total_seconds() / 3600)
        solar_altitude = calculate_solar_altitude(
                latitude=latitude,
                year=year,
                day_of_year=day_of_year,
                hour_of_year=hour_of_year,
                output_units=output_units,
                )
        solar_azimuth = calculate_solar_azimuth(
                latitude=latitude,
                year=year,
                day_of_year=day_of_year,
                hour_of_year=hour_of_year,
                output_units=output_units,
                )

    table = Table("Altitude", "Azimuth")
    table.add_row(str(solar_altitude), str(solar_azimuth))
    console.print(table)
    return solar_altitude, solar_azimuth

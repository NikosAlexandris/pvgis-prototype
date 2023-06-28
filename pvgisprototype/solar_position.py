import typer
from typing import Annotated
from typing import Optional
from enum import Enum
import numpy as np
import datetime
import suncalc
import pysolar
from .conversions import convert_to_degrees_if_requested
from .conversions import convert_to_radians_if_requested
from .conversions import convert_to_radians
from .timestamp import now_datetime
from .timestamp import convert_to_timezone
from .timestamp import attach_timezone
from .solar_altitude import calculate_solar_altitude
from .solar_azimuth import calculate_solar_azimuth
from .solar_declination import calculate_solar_declination
from .solar_geometry_pvgis import calculate_solar_position_pvgis
from .solar_geometry_pvgis import calculate_solar_time_pvgis
from .solar_geometry_pvgis_constants import calculate_solar_geometry_pvgis_constants


class SolarPositionModels(str, Enum):
    pysolar = 'pysolar'
    pvis = 'pvis'
    pvgis = 'PVGIS'
    suncalc = 'suncalc'
    skyfield = 'Skyfield'


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Calculate the solar altitude and azimuth for a day in the year",
)


@app.callback(invoke_without_command=True, no_args_is_help=True, context_settings={"ignore_unknown_options": True})
# @app.command('position', no_args_is_help=True, context_settings={"ignore_unknown_options": True})
def calculate_solar_position(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime.datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=convert_to_timezone)] = None,
        model: Annotated[SolarPositionModels, typer.Option(
            '-m',
            '--model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            help="Model to calculate solar position")] = SolarPositionModels.suncalc,
        output_units: Annotated[str, typer.Option(
            '-u',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar declination (degrees or radians)")] = 'radians',
        ):
    """
    """
    if model.value == SolarPositionModels.skyfield:
        solar_altitude, solar_azimuth, distance_to_sun = calculate_solar_position_skyfield(
                longitude,
                latitude,
                timestamp,
                timezone,
                # output_units,
                )
        solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, output_units)
        solar_altitude = convert_to_degrees_if_requested(solar_altitude, output_units)
    
    if model.value == SolarPositionModels.suncalc:
        # note : first azimuth, then altitude
        solar_azimuth, solar_altitude = suncalc.get_position(
                date=timestamp,  # this comes first here!
                lng=longitude,
                lat=latitude,
                ).values()
        solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, output_units)
        solar_altitude = convert_to_degrees_if_requested(solar_altitude, output_units)
    
    if model.value  == SolarPositionModels.pysolar:

        timestamp = attach_timezone(timestamp, timezone)
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

    if model.value  == SolarPositionModels.pvis:

        solar_altitude = calculate_solar_altitude(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                output_units=output_units,
                )
        solar_azimuth = calculate_solar_azimuth(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                output_units=output_units,
                )

    if model.value  == SolarPositionModels.pvgis:
        
        solar_declination = calculate_solar_declination(timestamp)
        local_solar_time = calculate_solar_time_pvgis(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                )

        solar_geometry_pvgis_day_constants = calculate_solar_geometry_pvgis_constants(
                longitude=longitude,
                latitude=latitude,
                local_solar_time=local_solar_time,
                solar_declination=solar_declination,
                )

        solar_altitude, solar_azimuth, sun_azimuth = calculate_solar_position_pvgis(
                solar_geometry_pvgis_day_constants,
                timestamp,
                )

        solar_altitude = convert_to_radians_if_requested(solar_altitude, output_units)
        solar_azimuth = convert_to_radians_if_requested(solar_azimuth, output_units)

    return solar_altitude, solar_azimuth

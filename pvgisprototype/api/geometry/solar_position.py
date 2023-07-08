from devtools import debug
import typer
from typing import Annotated
from typing import Optional
from typing import List
from enum import Enum
import numpy as np
import datetime
import suncalc
import pysolar
from ..utilities.conversions import convert_to_degrees_if_requested
from ..utilities.conversions import convert_to_radians_if_requested
from ..utilities.conversions import convert_to_radians
from ..utilities.timestamp import now_datetime
from ..utilities.timestamp import ctx_convert_to_timezone
from ..utilities.timestamp import attach_timezone
from .solar_altitude import calculate_solar_altitude
from .solar_azimuth import calculate_solar_azimuth
from .solar_declination import calculate_solar_declination
from .solar_geometry_skyfield import calculate_solar_position_skyfield
from .solar_geometry_skyfield import calculate_solar_altitude_azimuth_skyfield
from .solar_geometry_pvgis import calculate_solar_position_pvgis
from .solar_geometry_pvgis import calculate_solar_time_pvgis
from .solar_geometry_pvgis import calculate_solar_geometry_pvgis_constants
from .solar_position_noaa import calculate_solar_altitude_noaa
from .solar_position_noaa import calculate_solar_azimuth_noaa


class SolarPositionModels(str, Enum):
    all = 'all'
    noaa = 'NOAA'
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


def _parse_model(ctx: typer.Context, model: List[SolarPositionModels], param: typer.CallbackParam) -> List[SolarPositionModels]:

    print(f'ctx : {ctx}')
    print(f'param : {param}')
    print(f'model : {model}')
    print()
    if ctx.resilient_parsing:
        return
    if SolarPositionModels.all in model:
        # Return all models except for the 'all' itself!
        model = [model for model in SolarPositionModels if model != SolarPositionModels.all]
    print(f"Return model: {model}")
    return model


def model_solar_position(
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
            callback=ctx_convert_to_timezone)] = None,
        model: Annotated[SolarPositionModels, typer.Option(
            '-m',
            '--model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            help="Model to calculate solar position")] = SolarPositionModels.skyfield,
        apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
            '-a',
            '--atmospheric-refraction',
            help='Apply atmospheric refraction functions',
            )] = True,
        time_output_units: Annotated[str, typer.Option(
            '-u',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]")] = 'minutes',
        angle_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for internal calculations (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
        angle_output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for solar position calculations output (degrees or radians)")] = 'radians',
        ):
    """
    The solar altitude angle measures from the horizon up towards the zenith
    (positive, and down towards the nadir (negative)). The altitude is zero all
    along the great circle between zenith and nadir.

    The solar azimuth angle measures horizontally around the horizon from north
    through east, south, and west.

    Notes
    -----

    - All solar calculation functions return floating angular measurements in
      radians.
    """
    if model.value == SolarPositionModels.noaa:

        solar_altitude, units = calculate_solar_altitude_noaa(
                longitude,
                latitude,
                timestamp,
                timezone,
                output_units,
                )
        solar_altitude = convert_to_degrees_if_requested(solar_altitude, output_units)

        solar_azimuth, units = calculate_solar_azimuth_noaa(
                longitude,
                latitude,
                timestamp,
                timezone,
                apply_atmospheric_refraction,
                output_units,
                )
        solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, output_units)
    if model.value == SolarPositionModels.skyfield:
        solar_altitude, solar_azimuth = calculate_solar_altitude_azimuth_skyfield(
                longitude,
                latitude,
                timestamp,
                timezone,
                output_units,
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
                latitude_deg=latitude,  # this comes first
                longitude_deg=longitude,
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

        solar_altitude, _units = calculate_solar_altitude(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                output_units=output_units,
                )
        solar_azimuth, _units = calculate_solar_azimuth(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                output_units=output_units,
                )

    if model.value  == SolarPositionModels.pvgis:
        
        solar_declination = calculate_solar_declination(timestamp)
        local_solar_time, _units = calculate_solar_time_pvgis(
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

    return solar_altitude, solar_azimuth, output_units  # redesign a safer output_units!


@app.callback(invoke_without_command=True, no_args_is_help=True, context_settings={"ignore_unknown_options": True})
@app.command('position')
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
            callback=ctx_convert_to_timezone)] = None,
        models: Annotated[List[SolarPositionModels], typer.Option(
            '-m',
            '--models',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            callback=_parse_model,
            help="Model(s) to calculate solar position.")] = [SolarPositionModels.skyfield],
        output_units: Annotated[str, typer.Option(
            '-u',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar declination (degrees or radians)")] = 'radians',
):
    """
    Calculates the solar position using all models and returns the results in a table.
    """
    results = []
    for model in models:
        if model != SolarPositionModels.all:  # ignore 'all' in the enumeration
            solar_altitude, solar_azimuth, units = model_solar_position(
                longitude, latitude, timestamp, timezone, model, output_units
            )
            results.append({
                'Model': model.value,
                'Altitude': solar_altitude,
                'Azimuth': solar_azimuth,
                'Units': units,  # Don't trust me -- Redesign Me!
            })

    return results

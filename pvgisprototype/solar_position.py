import typer
from typing import Annotated
from enum import Enum
from datetime import datetime
from datetime import timezone
import suncalc
import pysolar
from pvgisprototype.solar_geometry import calculate_solar_altitude
from pvgisprototype.solar_geometry import calculate_solar_azimuth
from pvgisprototype.conversions import convert_to_degrees_if_requested
from pvgisprototype.conversions import convert_to_radians_if_requested


class SolarPositionModels(str, Enum):
    suncalc = 'suncalc'
    pysolar = 'pysolar'
    pvis = 'pvis'
    pvgis = 'pvgis'


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

    return solar_altitude, solar_azimuth

import typer
from typing import Annotated
from enum import Enum
from datetime import datetime
from datetime import timezone
import suncalc
import pysolar


class SolarPositionModels(str, Enum):
    suncalc = 'suncalc'
    pysolar = 'pysolar'


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
    help=f"Calculate the solar constant for a day in the year",
)


@app.callback(invoke_without_command=True, no_args_is_help=True)
def get_solar_position(
        longitude: float,
        latitude: float,
        timestamp: datetime,
        model: Annotated[SolarPositionModels, typer.Option(
            '--model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            help="Model to calculate solar position")] = 'suncalc',
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
        # note : first azimuth, the altitude
        solar_azimuth, solar_altitude = suncalc.get_position(
                date=timestamp,  # this comes first here!
                lng=longitude,
                lat=latitude,
                ).values()
    if model.value  == 'pysolar':
        solar_altitude = pysolar.solar.get_altitude(
                latitude_deg=longitude,  # this comes first
                longitude_deg=latitude,
                when=timestamp,
                )
        solar_azimuth = pysolar.solar.get_azimuth(
                latitude_deg=longitude,  # this comes first
                longitude_deg=latitude,
                when=timestamp,
                )
    # typer.echo(solar_altitude, solar_azimuth)
    print(solar_altitude, solar_azimuth)
    return solar_altitude, solar_azimuth

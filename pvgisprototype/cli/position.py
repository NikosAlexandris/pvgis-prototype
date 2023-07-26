from devtools import debug

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
from rich import box
from datetime import datetime
from zoneinfo import ZoneInfo
import math
import numpy as np
from ..api.utilities.timestamp import now_utc_datetimezone
from ..api.utilities.timestamp import now_local_datetimezone
from ..api.utilities.timestamp import ctx_convert_to_timezone
from ..api.utilities.timestamp import attach_timezone
from ..api.utilities.timestamp import convert_hours_to_seconds
from ..api.utilities.timestamp import random_datetimezone
from ..api.utilities.timestamp import ctx_attach_requested_timezone
from ..api.utilities.conversions import convert_to_radians
from ..api.utilities.conversions import convert_to_degrees_if_requested
from ..api.utilities.conversions import round_float_values
from ..api.geometry.solar_declination import calculate_solar_declination
from ..models.standard.solar_incidence import calculate_solar_incidence
from ..models.jenco.solar_incidence import calculate_solar_incidence_jenco
from ..models.jenco.solar_incidence import calculate_effective_solar_incidence_angle
from ..models.pyephem.solar_time import calculate_solar_time_ephem
from ..api.geometry.solar_hour_angle import calculate_hour_angle
from ..api.geometry.solar_hour_angle import calculate_hour_angle_sunrise
from ..api.geometry.solar_azimuth import calculate_solar_azimuth
from ..api.geometry.solar_models import SolarPositionModels
from ..api.geometry.solar_position import _parse_model
from ..api.geometry.solar_position import calculate_solar_position
from ..api.geometry.solar_position import model_solar_position
from ..models.noaa.solar_position import calculate_noaa_solar_position
from .rich_help_panel_names import rich_help_panel_geometry_time
from .rich_help_panel_names import rich_help_panel_geometry_position
from .rich_help_panel_names import rich_help_panel_geometry_refraction
from .rich_help_panel_names import rich_help_panel_geometry_surface

from pvgisprototype.api.input_models import HourAngleInput
from pvgisprototype.api.input_models import HourAngleSunriseInput


console = Console()
app = typer.Typer(
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":triangular_ruler:  Calculate solar geometry parameters for a location and moment in time",
)


state = {"verbose": False}
@app.callback()
def main(
        ctx: typer.Context,
        verbose: bool = False,
        ):
    """
    Solar position algorithms
    """
    # print(f"Executing command: {ctx.invoked_subcommand}")
    if verbose:
        print("Will output verbosely")
        state["verbose"] = True


@app.command(
        no_args_is_help=True,
        help=':sun: :clock12: :triangular_ruler: NOAA\'s general solar position calculations',
 )
def noaa(
        ctx: typer.Context,
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone,
            callback=ctx_attach_requested_timezone,
            )],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        refracted_solar_zenith: float = 1.5853349194640094,  # radians
        apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
            '-a',
            '--atmospheric-refraction',
            help='Apply atmospheric refraction functions',
            )] = True,
        time_output_units: Annotated[str, typer.Option(
            '-u',
            '--time-output-units',
            show_default=True,
            case_sensitive=False,
            help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]")] = 'minutes',
        angle_units: Annotated[str, typer.Option(
            '-u',
            '--angle-units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for internal calculations (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
        angle_output_units: Annotated[str, typer.Option(
            '-u',
            '--angle-output-units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for solar position calculations output (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
        rounding_places: Annotated[Optional[int], typer.Option(
            '-r',
            '--rounding-places',
            show_default=True,
            help='Number of places to round results to.')] = 5,
        verbose: bool = False,
        ):
    """
    """
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamp.tzinfo != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamp = timestamp
        user_requested_timezone = timezone

        timestamp = timestamp.astimezone(utc_zoneinfo)
        timezone = utc_zoneinfo
        typer.echo(f'The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!')

    solar_position_calculations = calculate_noaa_solar_position(
            longitude,
            latitude,
            timestamp,
            timezone,
            refracted_solar_zenith,
            apply_atmospheric_refraction,
            time_output_units,
            angle_units,
            angle_output_units,
            )
    debug(locals())

    # solar_position_calculations['fractional_year']
    # solar_position_calculations['equation_of_time']
    # solar_position_calculations['solar_declination']
    # solar_position_calculations['time_offset']
    # solar_position_calculations['true_solar_time']
    # solar_position_calculations['solar_hour_angle']
    # solar_position_calculations['solar_zenith']
    # solar_position_calculations['solar_altitude']
    # solar_position_calculations['solar_azimuth']
    # solar_position_calculations['sunrise_time']
    # solar_position_calculations['noon_time']
    # solar_position_calculations['local_solar_time']
    # solar_position_calculations['sunset_time']

    # Convert output timestamp back to the user-requested timezone
    try:
        timestamp = user_requested_timestamp
        timezone = user_requested_timezone
    except:
        print(f'I guess there where no user requested timestamp and zone')

    longitude = round_float_values(longitude, rounding_places)
    latitude = round_float_values(latitude, rounding_places)
    rounded_solar_position_calculations = round_float_values(solar_position_calculations, rounding_places)
    debug(locals())
    solar_position_table = Table(
            "Longitude",
            "Latitude",
            "Time",
            "Zone",
            "Model",
            # solar_position_calculations['fractional_year']
            # solar_position_calculations['equation_of_time']
            # solar_position_calculations['solar_declination']
            "Offset",
            # solar_position_calculations['time_offset']
            # solar_position_calculations['true_solar_time']
            # solar_position_calculations['solar_hour_angle']
            # solar_position_calculations['solar_zenith']
            "Altitude",
            "Azimuth",
            "Sunrise",
            'Noon',
            'Local solar time',
            "Sunset",
            box=box.SIMPLE_HEAD,
    )
    solar_position_table.add_row(
        str(longitude),
        str(latitude),
        str(timestamp),
        str(timezone),
        "NOAA",  # Model name
        str(solar_position_calculations['time_offset']),
        str(convert_to_degrees_if_requested(rounded_solar_position_calculations['solar_altitude'],
                                            'degrees')),
        str(rounded_solar_position_calculations['solar_azimuth']),
        str(solar_position_calculations['sunrise_time']),
        str(solar_position_calculations['noon_time']),
        str(solar_position_calculations['local_solar_time']),
        str(solar_position_calculations['sunset_time']),
    )
    if "user_requested_timestamp" in locals() and "user_requested_timezone" in locals():
        solar_position_table = Table(
                "Longitude",
                "Latitude",
                "Time",
                "Zone",
                "Local Time",
                "Local Zone",
                "Model",
                # solar_position_calculations['fractional_year']
                # solar_position_calculations['equation_of_time']
                # solar_position_calculations['solar_declination']
                # solar_position_calculations['time_offset']
                "Offset",
                # solar_position_calculations['true_solar_time']
                # solar_position_calculations['solar_hour_angle']
                # solar_position_calculations['solar_zenith']
                "Altitude",
                "Azimuth",
                "Sunrise",
                'Noon',
                'Local solar time',
                "Sunset",
                box=box.SIMPLE_HEAD,
                )
        solar_position_table.add_row(
            str(longitude),
            str(latitude),
            str(timestamp),
            str(timezone),
            str(user_requested_timestamp),
            str(user_requested_timezone),
            "NOAA",  # Model name
            str(solar_position_calculations['time_offset']),
            str(rounded_solar_position_calculations['solar_altitude']),
            str(rounded_solar_position_calculations['solar_azimuth']),
            str(solar_position_calculations['sunrise_time']),
            str(solar_position_calculations['noon_time']),
            str(solar_position_calculations['local_solar_time']),
            str(solar_position_calculations['sunset_time']),
        )

    console.print(solar_position_table)



# @app.callback(
#         'all',
#         invoke_without_command=True,
@app.command(
        'overview',
        no_args_is_help=True,
        help='⦩⦬ Calculate solar position parameters (altitude, azimuth)',
 )
def position(
        ctx: typer.Context,
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone,
            callback=ctx_attach_requested_timezone,
            )],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        model: Annotated[List[SolarPositionModels], typer.Option(
            '-m',
            '--model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            # callback=_parse_model,
            help="Model(s) to calculate solar position.")] = [SolarPositionModels.skyfield],
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
        rounding_places: Annotated[Optional[int], typer.Option(
            '-r',
            '--rounding-places',
            show_default=True,
            help='Number of places to round results to.')] = 5,
        verbose: bool = False,
        ):
    """
    """
    # print(f'Context: {ctx}')
    # print(f'Context: {ctx.params}')
    # print(f"Invoked subcommand: {ctx.invoked_subcommand}")

    # if ctx.invoked_subcommand is not None:
    #     print("Skipping default command to run sub-command.")
    #     return

    # elif ctx.invoked_subcommand in ['altitude', 'azimuth']:
    #     print('Execute subcommand')

    # else:
    #     print('Yay')
    #     return
    # Convert the input timestamp to UTC, for _all_ internal calculations
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamp.tzinfo != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamp = timestamp
        user_requested_timezone = timezone

        timestamp = timestamp.astimezone(utc_zoneinfo)
        timezone = utc_zoneinfo
        typer.echo(f'The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!')
    
    # Why does the callback function `_parse_model` not work? 
    if SolarPositionModels.all in model:
        model = [model for model in SolarPositionModels if model != SolarPositionModels.all]

    solar_position = calculate_solar_position(
            longitude,
            latitude,
            timestamp,
            timezone,
            model,
            apply_atmospheric_refraction,
            time_output_units,
            angle_units,
            angle_output_units,
            )
    longitude = round_float_values(longitude, rounding_places)
    latitude = round_float_values(latitude, rounding_places)
    rounded_solar_position = round_float_values(solar_position, rounding_places)
    solar_position_table = Table(
        "Longitude",
        "Latitude",
        "Time",
        "Zone",
        "Model",
        "Altitude",
        "Azimuth",
        "Units",
        box=box.SIMPLE_HEAD,
        )
    if "user_requested_timestamp" in locals() and "user_requested_timezone" in locals():
        solar_position_table = Table(
            "Longitude",
            "Latitude",
            "Time",
            "Zone",
            "Local Time",
            "Local Zone",
            "Model",
            "Altitude",
            "Azimuth",
            "Units",
            box=box.SIMPLE_HEAD,
            )
    for model_result in rounded_solar_position:
        model_name = model_result.get('Model', '')
        altitude = model_result.get('Altitude', '')
        azimuth = model_result.get('Azimuth', '')
        units = model_result.get('Units', '')
        # ---------------------------------------------------- Implement-Me---
        # Convert the result back to the user's time zone
        # output_timestamp = output_timestamp.astimezone(user_timezone)
        # --------------------------------------------------------------------

        # Redesign Me! =======================================================
        try:
            if (
                user_requested_timestamp in locals()
                and user_requested_timezone in locals()
            ):
                solar_position_table.add_row(
                    str(longitude),
                    str(latitude),
                    str(timestamp),
                    str(timezone),
                    str(user_requested_timestamp),
                    str(user_requested_timezone),
                    model_name,
                    str(altitude),
                    str(azimuth),
                    str(units),
                )
        except:
            pass
        #=====================================================================

        solar_position_table.add_row(
                str(longitude),
                str(latitude),
                str(timestamp),
                str(timezone),
                model_name,
                str(altitude),
                str(azimuth),
                str(units),
        )
    console.print(solar_position_table)


@app.command('altitude', no_args_is_help=True, help='⦩ Calculate the solar altitude')
def altitude(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone,
            callback=ctx_attach_requested_timezone,
            )],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        # model: Annotated[SolarPositionModels, typer.Option(
        #     '-m',
        #     '--model',
        #     show_default=True,
        #     show_choices=True,
        #     case_sensitive=False,
        #     # callback=_parse_model,
        #     help="Model(s) to calculate solar position.")] = SolarPositionModels.skyfield,
        model: Annotated[List[SolarPositionModels], typer.Option(
            '-m',
            '--model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            # callback=_parse_model,
            help="Model(s) to calculate solar position.")] = [SolarPositionModels.skyfield],
        apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
            '-a',
            '--atmospheric-refraction',
            help='Apply atmospheric refraction functions',
            )] = False,
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
        rounding_places: Annotated[Optional[int], typer.Option(
            '-r',
            '--rounding-places',
            show_default=True,
            help='Number of places to round results to.')] = 5,
        verbose: bool = False,
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
    # Convert the input timestamp to UTC, for _all_ internal calculations
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamp.tzinfo != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamp = timestamp
        user_requested_timezone = timezone

        timestamp = timestamp.astimezone(utc_zoneinfo)
        typer.echo(f'The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!')
    
    # debug(locals())
    # solar_altitude, _, units = model_solar_position(
    #         longitude,
    #         latitude,
    #         timestamp,
    #         timezone,
    #         model,
    #         apply_atmospheric_refraction,
    #         time_output_units,
    #         angle_units,
    #         angle_output_units,
    #         )
    # Why does the callback function `_parse_model` not work? 
    if SolarPositionModels.all in model:
        model = [model for model in SolarPositionModels if model != SolarPositionModels.all]

    solar_position = calculate_solar_position(
            longitude,
            latitude,
            timestamp,
            timezone,
            model,
            apply_atmospheric_refraction,
            time_output_units,
            angle_units,
            angle_output_units,
            )
    longitude = round_float_values(longitude, rounding_places)
    latitude = round_float_values(latitude, rounding_places)
    rounded_solar_position = round_float_values(solar_position, rounding_places)
    solar_position_table = Table(
        "Longitude",
        "Latitude",
        "Time",
        "Zone",
        "Model",
        "Altitude",
        "Units",
        box=box.SIMPLE_HEAD,
        )
    if "user_requested_timestamp" in locals() and "user_requested_timezone" in locals():
        solar_position_table = Table(
            "Longitude",
            "Latitude",
            "Time",
            "Zone",
            "Local Time",
            "Local Zone",
            "Model",
            "Altitude",
            "Units",
            box=box.SIMPLE_HEAD,
            )
    for model_result in rounded_solar_position:
        model_name = model_result.get('Model', '')
        altitude = model_result.get('Altitude', '')
        units = model_result.get('Units', '')
        # ---------------------------------------------------- Implement-Me---
        # Convert the result back to the user's time zone
        # output_timestamp = output_timestamp.astimezone(user_timezone)
        # --------------------------------------------------------------------

        # Redesign Me! =======================================================
        try:
            if (
                user_requested_timestamp in locals()
                and user_requested_timezone in locals()
            ):
                solar_position_table.add_row(
                    str(longitude),
                    str(latitude),
                    str(timestamp),
                    str(timezone),
                    str(user_requested_timestamp),
                    str(user_requested_timezone),
                    model_name,
                    str(altitude),
                    str(units),
                )
        except:
            pass
        #=====================================================================

        solar_position_table.add_row(
                str(longitude),
                str(latitude),
                str(timestamp),
                str(timezone),
                model_name,
                str(altitude),
                str(units),
        )
    console.print(solar_position_table)


@app.command('zenith', no_args_is_help=True, help=' Calculate the solar zenith')
def zenith(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone,
            callback=ctx_attach_requested_timezone,
            )],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        model: Annotated[SolarPositionModels, typer.Option(
            '-m',
            '--model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            # callback=_parse_model,
            help="Model(s) to calculate solar zenith.")] = SolarPositionModels.skyfield,
        apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
            '-a',
            '--atmospheric-refraction',
            help='Apply atmospheric refraction functions',
            )] = False,
        angle_output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar zenith (degrees or radians)")] = 'radians',
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
    # Convert the input timestamp to UTC, for _all_ internal calculations
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamp.tzinfo != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamp = timestamp
        user_requested_timezone = timezone

        timestamp = timestamp.astimezone(utc_zoneinfo)
        typer.echo(f'The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!')

    # debug(locals())
    solar_altitude, _ = model_solar_position(
        SolarPositionInput(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            model=model,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            angle_output_units=angle_output_units,
        )
    )

    solar_zenith = np.radians(90) - solar_altitude.value
    typer.echo(f'Solar zenith: {solar_zenith} {angle_output_units}')
    # return solar_zenith


@app.command('azimuth', no_args_is_help=True, help='⦬ Calculate the solar azimuth')
def azimuth(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone,
            callback=ctx_attach_requested_timezone,
            )],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        days_in_a_year: float = 365.25,
        perigee_offset: float = 0.048869,
        eccentricity: float = 0.01672,
        hour_offset: float = 0,
        model: Annotated[SolarPositionModels, typer.Option(
            '-m',
            '--model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            # callback=_parse_model,
            help="Model(s) to calculate solar azimuth.")] = SolarPositionModels.skyfield,
        apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
            '-a',
            '--atmospheric-refraction',
            help='Apply atmospheric refraction functions',
            )] = False,
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
            help="Angular units for the calculated solar azimuth output (degrees or radians)")] = 'radians',
        rounding_places: Annotated[Optional[int], typer.Option(
            '-r',
            '--rounding-places',
            show_default=True,
            help='Number of places to round results to.')] = 5,
        verbose: bool = False,
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
    # Convert the input timestamp to UTC, for _all_ internal calculations
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamp.tzinfo != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamp = timestamp
        user_requested_timezone = timezone

        timestamp = timestamp.astimezone(utc_zoneinfo)
        typer.echo(f'The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!')

    # debug(locals())
    _, solar_azimuth = model_solar_position(
        SolarPositionInput(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            model=model,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
        )
    )
    if verbose:
        typer.echo(f'Solar azimuth : {solar_azimuth.value} {solar_azimuth.unit}')
    else:
        typer.echo(f'{solar_azimuth.value} {solar_azimuth.unit}')
    # return solar_azimuth


@app.command('declination', no_args_is_help=True, help='∢ Calculate the solar declination')
def declination(
        timestamp: Annotated[datetime, typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        local: Annotated[bool, typer.Option(
            help='Use the system\'s local time zone',
            callback=now_local_datetimezone)] = False,
        days_in_a_year: float = 365.25,
        orbital_eccentricity: float = 0.03344,
        perigee_offset: float = 0.048869,
        angle_output_units: Annotated[Optional[str], typer.Option(
            '-u',
            '--angle-output-units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for solar position calculations output (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
        random_time: Annotated[bool, typer.Option(
            '-r',
            '--random',
            '--random-time',
            help="Generate a random date, time and timezone to demonstrate calculation")] = False,
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
    # Possible to move to a callback? ----------------------------------------
    if random_time:
        timestamp, timezone = random_datetimezone()
    # ------------------------------------------------------------------------

    # Convert the input timestamp to UTC, for _all_ internal calculations
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamp.tzinfo != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamp = timestamp
        user_requested_timezone = timezone

        timestamp = timestamp.astimezone(utc_zoneinfo)
        typer.echo(f'The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!')

    solar_declination = calculate_solar_declination(
            timestamp=timestamp,
            timezone=timezone,
            days_in_a_year=days_in_a_year,
            orbital_eccentricity=orbital_eccentricity,
            perigee_offset=perigee_offset,
            angle_output_units=angle_output_units,
    )

    typer.echo(f'Date, time and zone: {timestamp} {timezone}')
    typer.echo(f'Solar declination: {solar_declination.value} {solar_declination.unit}')            # FIXME: typer?
    # return solar_declination


@app.command('surface-orientation', no_args_is_help=True, help=':compass: Calculate the solar surface orientation (azimuth)')
def surface_orientation():
    """Calculate the surface azimuth angle

    The surface azimuth or orientation (also known as Psi) is the angle between
    the projection on a horizontal plane of the normal to a surface and the
    local meridian, with north through east directions being positive.
    """

    #
    # Update Me
    #

    pass


@app.command('surface-tilt', no_args_is_help=True, help='Calculate the solar surface tile (slope)')
def surface_tilt():
    """Calculate the surface tilt angle

    The surface tilt (or slope, also known as beta) is the angle between the
    plane of the surface and the horizontal plane. A horizontal surface has a
    slope of 0°, and a vertical surface has a slope of 90°.
    """

    #
    # Update Me
    #

    pass


@app.command('incidence', no_args_is_help=True, help='Calculate the solar incidence angle')
def incidence(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone,
            callback=ctx_attach_requested_timezone,
            )],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
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
            help="Output units for solar incidence angle (degrees or radians)")] = 'radians',
        ):
    """Calculate the angle of incidence

    The angle of incidence (also known as theta) is the angle between the
    direct beam of sunlight and the line perpendicular (normal) to the surface.
    If the sun is directly overhead and the surface is flat (horizontal), the
    angle of incidence is 0°.
    """

    #
    # Update Me
    #

    import random

    if not surface_tilt:
        surface_tilt = random.uniform(0, 90)  # Returns a random floating point number in the range [0, 90)

    if not surface_orientation:
        surface_orientation = random.uniform(0, 360)  # Returns a random floating point number in the range [0, 360)

    return None


@app.command('incidence-jenco', no_args_is_help=True, help='Calculate the solar incidence angle')
def incidence_jenco(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone,
            callback=ctx_attach_requested_timezone,
            )],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        random_time: Annotated[bool, typer.Option(
            '-r',
            '--random',
            '--random-time',
            help="Generate a random date, time and timezone to demonstrate calculation")] = False,
        hour_angle: Annotated[float, typer.Argument(
            help="Solar hour angle in radians")] = None,
        surface_tilt: Annotated[float, typer.Argument(
            help="Tilt of the surface in degrees")] = None,
        surface_orientation: Annotated[float, typer.Argument(
            help="Orientation of the surface (azimuth angle in degrees)")] = None,
        days_in_a_year: float = 365.25,
        orbital_eccentricity: float = 0.03344,
        perigee_offset: float = 0.048869,
        time_output_units: Annotated[str, typer.Option(
            '-u',
            '--time-output-units',
            show_default=True,
            case_sensitive=False,
            help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]")] = 'minutes',
        angle_units: Annotated[str, typer.Option(
            '-u',
            '--angle-units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for internal calculations (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
        angle_output_units: Annotated[str, typer.Option(
            '-u',
            '--angle-output-units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for solar position calculations output (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
        rounding_places: Annotated[Optional[int], typer.Option(
            '-r',
            '--rounding-places',
            show_default=True,
            help='Number of places to round results to.')] = 5,
        verbose: bool = False,
        ):
    """Calculate the angle of incidence

    The angle of incidence (also known as theta) is the angle between the
    direct beam of sunlight and the line perpendicular (normal) to the surface.
    If the sun is directly overhead and the surface is flat (horizontal), the
    angle of incidence is 0°.
    """

    # --------------------------------------------------------------- Idea ---
    # if not given, optimise tilt and orientation... ?
    # ------------------------------------------------------------------------
    import random

    if not surface_tilt:
        surface_tilt = random.uniform(0, 90)

    if not surface_orientation:
        surface_orientation = random.uniform(0, 360)

    solar_incidence_angle = calculate_solar_incidence_jenco(
        longitude,
        latitude,
        timestamp,
        timezone,
        random_time,
        hour_angle,
        surface_tilt,
        surface_orientation,
        days_in_a_year,
        orbital_eccentricity,
        perigee_offset,
        time_output_units,
        angle_units,
        angle_output_units,
        rounding_places,
        verbose,
    )

    typer.echo(f'Solar incidence angle {solar_incidence_angle} {angle_output_units}')


@app.command(
    'incidence-effective',
    no_args_is_help=True,
    help='Calculate the effective solar incidence angle considering shadows',
)
def incidence_jenco(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
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
            help="Output units for solar incidence angle (degrees or radians)")] = 'radians',
        ):
    """Calculate the angle of incidence

    The angle of incidence (also known as theta) is the angle between the
    direct beam of sunlight and the line perpendicular (normal) to the surface.
    If the sun is directly overhead and the surface is flat (horizontal), the
    angle of incidence is 0°.
    """
    effective_solar_incidence_angle = calculate_effective_solar_incidence_angle(
        longitude,
        latitude,
        hour_angle,
        surface_tilt,
        surface_orientation,
        solar_azimuth,
        solar_altitude,
        shadow_indicator,
        horizon_heights,
        horizon_interval,
    )

    return effective_solar_incidence_angle


@app.command('hour-angle', no_args_is_help=True, help=':clock12: :globe_with_meridians: Calculate the hour angle (ω)')
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
    """Calculate the hour angle 'ω = (ST / 3600 - 12) * 15 * π / 180'

    The hour angle (ω) is the angle at any instant through which the earth has
    to turn to bring the meridian of the observer directly in line with the
    sun's rays measured in radian. In other words, it is a measure of time,
    expressed in angular measurement, usually degrees, from solar noon. It
    increases by 15° per hour, negative before solar noon and positive after
    solar noon.
    """

    #
    # Update Me
    #

    hour_angle = calculate_hour_angle(
        HourAngleInput(
            solar_time=solar_time,
            angle_output_units=output_units,
        )
    )
    typer.echo(f'Hour angle: {hour_angle.value} {hour_angle.unit}')              # FIXME: typer ?!


@app.command('sunrise', no_args_is_help=True, help=':sunrise: Calculate the hour angle (ω) at sun rise and set')
def hour_angle(
        latitude: Annotated[Optional[float], typer.Argument(
            min=-90, max=90)],
        surface_tilt: Annotated[Optional[float], typer.Argument(
            min=0, max=90)] = 0,
        solar_declination: Annotated[Optional[float], typer.Argument(
            min=-90, max=90)] = 0,                                                  # XXX: Default value changed from 180 to 0
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ):
    """Calculate the hour angle 'ω = (ST / 3600 - 12) * 15 * π / 180'

    The hour angle (ω) is the angle at any instant through which the earth has
    to turn to bring the meridian of the observer directly in line with the
    sun's rays measured in radian. In other words, it is a measure of time,
    expressed in angular measurement, usually degrees, from solar noon. It
    increases by 15° per hour, negative before solar noon and positive after
    solar noon.
    """

    #
    # Update Me
    #

    hour_angle = calculate_hour_angle_sunrise(
        HourAngleSunriseInput(
            latitude=latitude,
            surface_tilt=surface_tilt,
            solar_declination=solar_declination,
            angle_output_units=output_units,
        )
    )

    typer.echo(f'Solar time: {hour_angle.value} {hour_angle.unit}')              # FIXME: typer ?


if __name__ == "__main__":
    # import sys
    # commands = {'all', 'altitude', 'azimuth'}
    # sys.argv.insert(1, 'all') if sys.argv[1] not in commands else None
    # debug(locals())
    app()

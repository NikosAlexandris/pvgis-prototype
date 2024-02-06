import typer
from typer.core import TyperGroup
from click import Context
from typing import Annotated
from typing import Optional
from typing import List
# from typing import Path
from datetime import datetime
from pathlib import Path
import numpy as np
from pvgisprototype.api.utilities.conversions import convert_to_radians
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import ctx_attach_requested_timezone
from pvgisprototype.api.utilities.timestamp import ctx_convert_to_timezone
from pvgisprototype.api.utilities.timestamp import now_local_datetimezone
from pvgisprototype.api.utilities.timestamp import convert_hours_to_datetime_time
from pvgisprototype.api.utilities.timestamp import callback_generate_datetime_series
from pvgisprototype.api.utilities.timestamp import parse_timestamp_series
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_advanced_options
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_geometry_surface
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_solar_position
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_solar_time
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_earth_orbit
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_atmospheric_properties
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_output
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_time_series
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_time_series_selection
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_plotting
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_efficiency
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.api.geometry.models import SolarIncidenceModel
from pvgisprototype.constants import LATITUDE_MINIMUM
from pvgisprototype.constants import LATITUDE_MAXIMUM
from pvgisprototype.constants import LONGITUDE_MINIMUM
from pvgisprototype.constants import LONGITUDE_MAXIMUM
from pvgisprototype.constants import ELEVATION_MINIMUM
from pvgisprototype.constants import ELEVATION_MAXIMUM
from pvgisprototype.constants import SOLAR_DECLINATION_MINIMUM
from pvgisprototype.constants import SOLAR_DECLINATION_MAXIMUM
from pvgisprototype.constants import SURFACE_TILT_MINIMUM
from pvgisprototype.constants import SURFACE_TILT_MAXIMUM
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_MINIMUM
from pvgisprototype.constants import SURFACE_ORIENTATION_MAXIMUM
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT_MINIMUM
from pvgisprototype.constants import DAYS_IN_A_YEAR
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import TEMPERATURE_DEFAULT
from pvgisprototype.constants import TEMPERATURE_UNIT
from pvgisprototype.constants import WIND_SPEED_DEFAULT
from pvgisprototype.constants import WIND_SPEED_UNIT
from pvgisprototype.constants import LINKE_TURBIDITY_MINIMUM
from pvgisprototype.constants import LINKE_TURBIDITY_MAXIMUM
from pvgisprototype.constants import LINKE_TURBIDITY_DEFAULT
from pvgisprototype.constants import LINKE_TURBIDITY_UNIT
from pvgisprototype.constants import OPTICAL_AIR_MASS_DEFAULT
from pvgisprototype.constants import OPTICAL_AIR_MASS_UNIT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype import TemperatureSeries
from pvgisprototype import WindSpeedSeries
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype import OpticalAirMass
from pvgisprototype.validation.pvis_data_classes import BaseTimestampSeriesModel


class OrderCommands(TyperGroup):
  def list_commands(self, ctx: Context):
    """Return list of commands in the order appear.
    See: https://github.com/tiangolo/typer/issues/428#issuecomment-1238866548
    """
    return list(self.commands)


# Generic

def _version_callback(flag: bool) -> None:
    if flag:
        from pvgisprototype._version import __version__
        print(f"PVGIS prototype version: {__version__}")
        raise typer.Exit(code=0)


typer_option_version = typer.Option(
    "--version",
    help="Show the version of the application and exit",
    callback=_version_callback,
    is_eager=True,
    # default_factory=None,
)

typer_option_log = typer.Option(
    '--log',
    '-l',
    help="Enable logging",
    # help="Specify a log file to write logs to, or omit for stderr.")] = None,
    is_flag=True,
    # default_factory=False,
)


# Where?

longitude_typer_help=f'Longitude in decimal degrees ranging in [-180, 360]. [yellow]If ranging in [0, 360], consider the `--convert-longitude-360` option.[/yellow]'
typer_argument_longitude = typer.Argument(
    help=longitude_typer_help,
    min=LONGITUDE_MINIMUM,
    max=LONGITUDE_MAXIMUM,
    callback=convert_to_radians,
    # callback=convert_to_Longitude,
    show_default=False,
)
typer_argument_longitude_in_degrees = typer.Argument(
    help=longitude_typer_help,
    min=LONGITUDE_MINIMUM,
    max=LONGITUDE_MAXIMUM,
    show_default=False,
)
latitude_typer_help='Latitude in decimal degrees ranging in [-90, 90]'
typer_argument_latitude = typer.Argument(
    help=latitude_typer_help,
    min=LATITUDE_MINIMUM,
    max=LATITUDE_MAXIMUM,
    callback=convert_to_radians,
    show_default=False,
)
typer_argument_latitude_in_degrees = typer.Argument(
    help=latitude_typer_help,
    min=LATITUDE_MINIMUM,
    max=LATITUDE_MAXIMUM,
    show_default=False,
)
typer_argument_elevation = typer.Argument(
    help='Topographical elevation',
    min=ELEVATION_MINIMUM,
    max=ELEVATION_MAXIMUM,
    # rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory=0,
    show_default=False,
)
typer_argument_horizon_heights = typer.Option(
    help='List of horizon heights (comma-separated values or .csv file) at equal angular distance around the horizon given in clockwise direction starting at North, going to East, South, West, and back to North (first point is due north, last is west of north). Example: 10, 20, 30, 20, 5, 0, 10, 20, 5, 0, 10, 20, 30, 20, 5, 0, 10, 20, 5, 0',
    # default_factory = None,
    show_default=False,
)
typer_argument_pv_technology = typer.Argument(
    help='Technology of the PV module: crystalline silicon cells, thin film modules made from CIS or CIGS, thin film modules made from Cadmium Telluride (CdTe), other/unknown',
    show_default=False,
)
typer_argument_mounting_type = typer.Argument(
    help='Type of mounting',  # in PVGIS : mountingplace
    # default_factory = 'free',  # see PVGIS for more!
    show_default=False,
)
typer_argument_area = typer.Argument(
    help='The area of the modules in m<sup>2</sup>',
    min=0.001,  # min of mini-solar-panel?
    # rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = None,
    show_default=False,
)

# When?

timestamp_typer_help = "Quoted date-time string of data to extract from series, example: [yellow]'2112-12-21 21:12:12'[/yellow]'"
typer_argument_timestamp = typer.Argument(
    help=timestamp_typer_help,
    callback=ctx_attach_requested_timezone,
    # rich_help_panel=rich_help_panel_time_series,
    default_factory=now_utc_datetimezone,
    show_default=False,
)
timestamps_typer_help = "Quoted date-time strings of data to extract from series, example: [yellow]'2112-12-21, 2112-12-21 12:21:21, 2112-12-21 21:12:12'[/yellow]'"
typer_argument_timestamps = typer.Argument(
    help=timestamps_typer_help,
    parser=parse_timestamp_series,
    callback=callback_generate_datetime_series,
#     default_factory=now_utc_datetimezone_series,
    show_default=False,
)
typer_option_timestamps = typer.Option(
    help='Timestamps',
    parser=parse_timestamp_series,
    callback=callback_generate_datetime_series,
#     default_factory=now_utc_datetimezone_series,
)
warning_overrides_timestamps = f'[yellow]Overrides the `timestamps` parameter![/yellow]'
typer_option_start_time = typer.Option(
    help=f'Start timestamp of the period. {warning_overrides_timestamps}',
    rich_help_panel=rich_help_panel_time_series,
    default_factory = None,
)
typer_option_frequency = typer.Option(
    help=f"Frequency for timestamp generation, ex. 30m. A number and date/time unit : (D)ay, (M)onth, (Y)ear, (h)ours, (m)inutes, or (s)econds. See NumPy's timedelta64.",
    rich_help_panel=rich_help_panel_time_series,
    # default_factory='h'
)
typer_option_end_time = typer.Option(
    help=f'End timestamp of the period. {warning_overrides_timestamps}',
    rich_help_panel=rich_help_panel_time_series,
    default_factory = None,
)
typer_option_timezone = typer.Option(
    # help='Timezone (e.g., "Europe/Athens"). Set _local_ to use the system\'s time zone',
    help="Timezone (e.g., 'Europe/Athens'). Use the system's time zone via the --local option.",
    callback=ctx_convert_to_timezone,
    # default_factory=None,
)
typer_option_local_time = typer.Option(
    help="Use the system's local time zone",
    callback=now_local_datetimezone
)
typer_option_random_time = typer.Option(
    # '--random-time',
    # '--random',
    help='Generate a random date, time and timezone to demonstrate calculation'
)
typer_option_random_day = typer.Option(
    # '--random-day',
    # '--random',
    help='Generate a random day to demonstrate calculation',
    # default_factory=RANDOM_DAY_FLAG_DEFAULT,
)
typer_option_random_days = typer.Option(
    # '--random-day',
    # '--random',
    help='Generate random days to demonstrate calculation',
    # default_factory=RANDOM_DAY_FLAG_DEFAULT,
)

# Time series

time_series_typer_help='A time series dataset (any format supported by Xarray)'
typer_argument_time_series = typer.Argument(
    help=time_series_typer_help,
    # rich_help_panel=rich_help_panel_time_series,
    show_default=False,
)
typer_option_time_series = typer.Option(
    help=time_series_typer_help,
    show_default=False,
    rich_help_panel=rich_help_panel_time_series,
)
typer_option_data_variable = typer.Option(
    help='Variable name',
    show_default=False,
    rich_help_panel=rich_help_panel_time_series,
)
typer_option_mask_and_scale = typer.Option(
    help="Mask and scale the series",
    rich_help_panel=rich_help_panel_time_series,
    # default_factory=False,
)
typer_option_nearest_neighbor_lookup = typer.Option(
    help='Enable nearest neighbor (inexact) lookups. Read Xarray manual on [underline]nearest-neighbor-lookups[/underline]',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_time_series_selection,
    # default_factory=None, # default_factory=MethodsForInexactMatches.nearest,
)
typer_option_inexact_matches_method = typer.Option(
    help='Method for nearest neighbor (inexact) lookups. Read Xarray manual on [underline]nearest-neighbor-lookups[/underline]',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_time_series_selection,
    # default_factory=MethodsForInexactMatches.nearest,
)
typer_option_tolerance = typer.Option(
    help=f'Maximum distance between original & new labels for inexact matches. Read Xarray manual on [underline]nearest-neighbor-lookups[/underline]',
    #  https://docs.xarray.dev/en/stable/user-guide/indexing.html#nearest-neighbor-lookups',
    rich_help_panel=rich_help_panel_time_series_selection,
    # default_factory=0.1,
)


# Solar geometry

typer_argument_solar_declination = typer.Argument(
    help='Solar declination angle',
    min=SOLAR_DECLINATION_MINIMUM,
    max=SOLAR_DECLINATION_MAXIMUM,
    callback=convert_to_radians,
    show_default=False,
)
typer_option_solar_declination = typer.Option(
    help='Solar declination angle',
    min=SOLAR_DECLINATION_MINIMUM,
    max=SOLAR_DECLINATION_MAXIMUM,
    callback=convert_to_radians,
)
typer_option_solar_declination_model = typer.Option(
    help='Model to calculate the solar declination angle',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    # callback=_parse_model,  # This did not work!
    # help="Model(s) to calculate solar declination."
    # rich_help_panel=rich_help_panel_solar_declination,
    rich_help_panel=rich_help_panel_solar_position,
)

solar_constant_typer_help='Top-of-Atmosphere mean solar electromagnetic radiation (W/m-2) 1 au (astronomical unit) away from the Sun.'  #  (~1360.8 W/m2)
typer_argument_solar_constant = typer.Argument(
    help=solar_constant_typer_help,
    min=SOLAR_CONSTANT_MINIMUM,
    rich_help_panel=rich_help_panel_earth_orbit,
    # default_factory = SOLAR_CONSTANT,
    show_default=False,
)
typer_option_solar_constant = typer.Option(
    help=solar_constant_typer_help,
    min=SOLAR_CONSTANT_MINIMUM,
    rich_help_panel=rich_help_panel_earth_orbit,
    # default_factory = SOLAR_CONSTANT,
)

SOLAR_INCIDENCE_ANGLE_MODEL_DEFAULT=SolarIncidenceModel.jenco
typer_option_solar_incidence_model = typer.Option(
    '--solar-incidence-model',
    help='Method to calculate the solar incidence angle',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_solar_position,
    # default_factory=SOLAR_INCIDENCE_ANGLE_MODEL_DEFAULT,
)

# Solar surface

def surface_tilt_callback(
    ctx: typer.Context,
    # param: typer.CallbackParam,
    surface_tilt: float,
) -> float:
    """Set the default surface tilt equal to the latitude"""
    if ctx.resilient_parsing:
        return
    # if type(latitude) != float:
    #     raise typer.BadParameter("Input should be a float!")
    if not surface_tilt:
        surface_tilt = ctx.params.get('latitude')
        from rich import print
        print(f'[yellow]* Surface tilt set to match the input latitude[/yellow]!')
    else:
        surface_tilt = np.radians(surface_tilt)

    return surface_tilt


surface_tilt_typer_help='Solar surface tilt angle from the horizontal plane'  # in PVGIS : slope
typer_argument_surface_tilt = typer.Argument(
    help=surface_tilt_typer_help,
    min=SURFACE_TILT_MINIMUM,
    max=SURFACE_TILT_MAXIMUM,
    callback=surface_tilt_callback,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_TILT_DEFAULT,
    show_default=False,
)
typer_option_surface_tilt = typer.Option(
    help=surface_tilt_typer_help,
    min=SURFACE_TILT_MINIMUM,
    max=SURFACE_TILT_MAXIMUM,
    callback=surface_tilt_callback,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_TILT_DEFAULT,
)
typer_option_random_surface_tilt = typer.Option(
    help='Random solar surface tilt angle',
    # min=SURFACE_TILT_MINIMUM,
    # max=SURFACE_TILT_MAXIMUM,
    # callback=random_surface_tilt,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_TILT_DEFAULT,
)
typer_option_optimise_surface_tilt = typer.Option(
    help='Optimise inclination for a fixed PV system',  # in PVGIS : optimalinclination
    # default_factory = OPTIMISE_SURFACE_TILT_FLAG_DEFAULT,
)
typer_option_optimise_surface_geometry = typer.Option(
    help='Optimise inclination and orientation for a fixed PV system',  # in PVGIS : optimalangles
    # default_factory = OPTIMISE_SURFACE_GEOMETRY_FLAG_DEFAULT,
)
surface_orientation_typer_help='Solar surface orientation angle. [yellow]Due north is 0 degrees.[/yellow]'  # also known as : azimuth, in PVGIS : aspect
# Note, in PVGIS : '0=south, 90=west, -90=east' ? ----------------------------
typer_argument_surface_orientation = typer.Argument(
    help=surface_orientation_typer_help,
    min=SURFACE_ORIENTATION_MINIMUM,
    max=SURFACE_ORIENTATION_MAXIMUM,
    callback=convert_to_radians,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_ORIENTATION_DEFAULT,
    show_default=False,
)
typer_option_surface_orientation = typer.Option(
    help=surface_orientation_typer_help,
    min=SURFACE_ORIENTATION_MINIMUM,
    max=SURFACE_ORIENTATION_MAXIMUM,
    callback=convert_to_radians,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_ORIENTATION_DEFAULT,
)
typer_option_random_surface_orientation = typer.Option(
    help='Random solar surface orientation angle. [yellow]Due north is 0 degrees.[/yellow]',
    # min=SURFACE_ORIENTATION_MINIMUM,
    # max=SURFACE_ORIENTATION_MAXIMUM,
    # callback=random_surface_orientation,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_ORIENTATION_DEFAULT,
)

typer_argument_true_solar_time = typer.Argument(
    help='The apparent (or true) solar time in decimal hours on a 24 hour base',
    callback=convert_hours_to_datetime_time,
    rich_help_panel=rich_help_panel_solar_time,
    show_default=False,
)
typer_argument_hour_angle = typer.Argument(
    help="Solar hour angle in radians",
    min=0,
    max=1,
    # default_factory=None,
    show_default=False,
)


# Solar position

typer_option_solar_position_model = typer.Option(
    '--solar-position-model',
    help='Model to calculate solar position',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    # callback=_parse_model,  # This did not work!
    # help="Model(s) to calculate solar position."
    rich_help_panel=rich_help_panel_solar_position,
)

typer_argument_solar_altitude = typer.Argument(
    help='Solar altitude',
    rich_help_panel=rich_help_panel_solar_position,
    show_default=False,
)
typer_argument_solar_altitude_series = typer.Argument(
    help='Solar altitude series',
    rich_help_panel=rich_help_panel_solar_position,
    show_default=False,
)
typer_argument_refracted_solar_altitude = typer.Argument(
    help='Refracted solar altitude',
    rich_help_panel=rich_help_panel_solar_position,
)
typer_argument_refracted_solar_altitude_series = typer.Argument(
    help='Refracted solar altitude',
    rich_help_panel=rich_help_panel_solar_position,
)
typer_argument_solar_incidence = typer.Argument(
    help='Solar incidence',
    rich_help_panel=rich_help_panel_solar_position,
    show_default=False,
)
typer_argument_solar_incidence_series = typer.Argument(
    help='Solar incidence series',
    rich_help_panel=rich_help_panel_solar_position,
    show_default=False,
)

# Solar time

typer_option_solar_time_model = typer.Option(
    '--solar-time-model',
    help="Model to calculate solar time",
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_solar_time,
    # default_factory=[SolarTimeModel.skyfield],
)
typer_option_global_time_offset = typer.Option(
    help='Global time offset',
    rich_help_panel=rich_help_panel_solar_time,
    # default_factory=0,
)
typer_option_hour_offset = typer.Option(
    help='Hour offset',
    rich_help_panel=rich_help_panel_solar_time,
    # default_factory=0
)


# Earth orbit

typer_option_days_in_a_year = typer.Option(
    help='Number of days in a year',
    rich_help_panel=rich_help_panel_earth_orbit,
    # default_factory=DAYS_IN_A_YEAR,
)
typer_option_perigee_offset = typer.Option(
    help='Perigee offset',
    rich_help_panel=rich_help_panel_earth_orbit,
    # default_factory=PERIGEE_OFFSET,
)
typer_option_eccentricity_correction_factor = typer.Option(
    help='Eccentricity correction factor',
    rich_help_panel=rich_help_panel_earth_orbit,
    # default_factory=0.ECCENTRICITY_CORRECTION_FACTOR,
)


# Atmospheric properties

def parse_temperature_series(temperature_input: int):     # FIXME: Re-design ?
    try:
        if isinstance(temperature_input, str):
            temperature_input = np.fromstring(temperature_input, sep=',', dtype=float)
        else:
            temperature_input = np.array(temperature_input, dtype=float)

        return temperature_input

    except ValueError as e:  # conversion to float failed
        print(f"Error parsing input: {e}")
        return None


def temperature_series_argument_callback(
    ctx: Context,
    temperature_series: TemperatureSeries,
):
    reference_series = ctx.params.get('timestamps')
    if temperature_series == TEMPERATURE_DEFAULT:
        temperature_series = np.full(len(reference_series), TEMPERATURE_DEFAULT, dtype=float)

    if temperature_series.size != len(reference_series):
        raise ValueError(f"The number of temperature values ({temperature_series.size}) does not match the number of irradiance values ({len(reference_series)}).")

    return TemperatureSeries(value=temperature_series, unit=TEMPERATURE_UNIT)


def temperature_series_callback(
    ctx: Context,
    temperature_series: TemperatureSeries,
):
    reference_series = ctx.params.get('irradiance_series')
    # if not reference_series:
    #     reference_series = ctx.params.get('irradiance_series')

    if temperature_series == TEMPERATURE_DEFAULT:
        temperature_series = np.full(len(reference_series), TEMPERATURE_DEFAULT, dtype=float)

    if temperature_series.size != len(reference_series):
        raise ValueError(f"The number of temperature values ({temperature_series.size}) does not match the number of irradiance values ({len(reference_series)}).")

    return TemperatureSeries(value=temperature_series, unit=TEMPERATURE_UNIT)


temperature_typer_help='Ambient temperature time series'
typer_argument_temperature_series = typer.Option(
    help=temperature_typer_help,
    # min=TEMPERATURE_MINIMUM,
    # max=TEMPERATURE_MAXIMUM,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # is_eager=True,
    parser=parse_temperature_series,
    callback=temperature_series_argument_callback,
    # default_factory=TEMPERATURE_DEFAULT,
    show_default=False,
)
typer_option_temperature_series = typer.Option(
    help=temperature_typer_help,
    # min=TEMPERATURE_MINIMUM,
    # max=TEMPERATURE_MAXIMUM,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # is_eager=True,
    parser=parse_temperature_series,
    callback=temperature_series_callback,
    # default_factory=TEMPERATURE_DEFAULT,
)


def parse_wind_speed_series(wind_speed_input: int):     # FIXME: Re-design ?
    try:
        if isinstance(wind_speed_input, str):
            wind_speed_input = np.fromstring(wind_speed_input, sep=',', dtype=float)
        else:
            wind_speed_input = np.array(wind_speed_input, dtype=float)
        return wind_speed_input

    except ValueError as e:  # conversion to float failed
        print(f"Error parsing input: {e}")
        return None


def wind_speed_series_argument_callback(
    ctx: Context,
    wind_speed_series: WindSpeedSeries,
    param: typer.CallbackParam,
):
    reference_series = ctx.params.get('timestamps')
    # if not reference_series:
    #     reference_series = ctx.params.get('irradiance_series')

    if wind_speed_series == WIND_SPEED_DEFAULT:
        wind_speed_series = np.full(len(reference_series), WIND_SPEED_DEFAULT, dtype=float)

    if wind_speed_series.size != len(reference_series):
        raise ValueError(f"The number of wind_speed values ({wind_speed_series.size}) does not match the number of irradiance values ({len(reference_series)}).")
    return WindSpeedSeries(value=wind_speed_series, unit=WIND_SPEED_UNIT)


def wind_speed_series_callback(
    ctx: Context,
    wind_speed_series: WindSpeedSeries,
    param: typer.CallbackParam,
):
    reference_series = ctx.params.get('irradiance_series')
    # if not reference_series:
    #     reference_series = ctx.params.get('irradiance_series')

    if wind_speed_series == WIND_SPEED_DEFAULT:
        wind_speed_series = np.full(len(reference_series), WIND_SPEED_DEFAULT, dtype=float)

    if wind_speed_series.size != len(reference_series):
        raise ValueError(f"The number of wind_speed values ({wind_speed_series.size}) does not match the number of irradiance values ({len(reference_series)}).")
    return WindSpeedSeries(value=wind_speed_series, unit=WIND_SPEED_UNIT)


wind_speed_typer_help='Ambient wind_speed time series'
typer_argument_wind_speed_series = typer.Option(
    help=wind_speed_typer_help,
    # min=WIND_SPEED_MINIMUM,
    # max=WIND_SPEED_MAXIMUM,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # is_eager=True,
    parser=parse_wind_speed_series,
    callback=wind_speed_series_argument_callback,
    # default_factory=WIND_SPEED_DEFAULT,
    show_default=False,
)
typer_option_wind_speed_series = typer.Option(
    help=wind_speed_typer_help,
    # min=WIND_SPEED_MINIMUM,
    # max=WIND_SPEED_MAXIMUM,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # is_eager=True,
    parser=parse_wind_speed_series,
    callback=wind_speed_series_callback,
    # default_factory=WIND_SPEED_DEFAULT,
)

## Linke turbidity

def parse_linke_turbidity_factor_series(linke_turbidity_factor_input: str):     # FIXME: Re-design ?
    try:
        if isinstance(linke_turbidity_factor_input, str):
            linke_turbidity_factor_input = np.fromstring(linke_turbidity_factor_input, sep=',', dtype=float)
        else:
            linke_turbidity_factor_input = np.array(linke_turbidity_factor_input, dtype=float)

        return linke_turbidity_factor_input

    except ValueError as e:  # conversion to float failed
        print(f"Error parsing input: {e}")
        return None


def linke_turbidity_factor_callback(ctx: Context, value: np.array):
    if np.any(value):
        return LinkeTurbidityFactor(value=value, unit=LINKE_TURBIDITY_UNIT)
    else:
        timestamps = ctx.params.get('timestamps')
        linke_turbidity = np.array([LINKE_TURBIDITY_DEFAULT for _ in timestamps])
        return LinkeTurbidityFactor(value=linke_turbidity, unit=LINKE_TURBIDITY_UNIT)


linke_turbidity_factor_typer_help='Ratio of total to Rayleigh optical depth measuring atmospheric turbidity'
typer_argument_linke_turbidity_factor = typer.Argument(
    help=linke_turbidity_factor_typer_help,
    min=LINKE_TURBIDITY_MINIMUM,
    max=LINKE_TURBIDITY_MAXIMUM,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    parser=parse_linke_turbidity_factor_series,
    callback=linke_turbidity_factor_callback,
    # default_factory=LINKE_TURBIDITY_DEFAULT,
    show_default=False,
)
typer_option_linke_turbidity_factor = typer.Option(
    help=linke_turbidity_factor_typer_help,
    min=LINKE_TURBIDITY_MINIMUM,
    max=LINKE_TURBIDITY_MAXIMUM,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    parser=parse_linke_turbidity_factor_series,
    callback=linke_turbidity_factor_callback,
    # default_factory=LINKE_TURBIDITY_DEFAULT,
)

linke_turbidity_factor_series_typer_help='Ratio series of total to Rayleigh optical depth measuring atmospheric turbidity'
typer_option_linke_turbidity_factor_series = typer.Option(
    help=linke_turbidity_factor_typer_help,
    # min=LINKE_TURBIDITY_MINIMUM,
    # max=LINKE_TURBIDITY_MAXIMUM,
    parser=parse_linke_turbidity_factor_series,
    callback=linke_turbidity_factor_callback,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=LINKE_TURBIDITY_DEFAULT,
)

## Optical air mass

def parse_optical_air_mass(optical_air_mass_input: str):
    if isinstance(optical_air_mass_input, str):
        optical_air_mass_strings = optical_air_mass_input.split(',')
        return optical_air_mass_strings
    else:
        return optical_air_mass_input


def optical_air_mass_callback(value: str, ctx: Context):
    """Callback to handle the optical air mass series input or provide a default series."""
    if value:
        return OpticalAirMass(value=value, unit=OPTICAL_AIR_MASS_UNIT)


typer_option_optical_air_mass = typer.Option(
    help=f'Relative optical air mass [{OPTICAL_AIR_MASS_UNIT}]',
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=OPTICAL_AIR_MASS_DEFAULT,
    callback=optical_air_mass_callback,
)

## Optical air mass series

def parse_optical_air_mass_series(optical_air_mass_factor_input: str) -> List[float]:
    """Parse a string of optical air mass values separated by commas into a list of floats."""
    if isinstance(optical_air_mass_factor_input, str):
        optical_air_mass_factor_strings = optical_air_mass_factor_input.split(',')
        optical_air_mass_factor_series = [optical_air_mass_factor for optical_air_mass_factor in optical_air_mass_factor_strings]
        return optical_air_mass_factor_series
    else:
        return optical_air_mass_factor_input


def optical_air_mass_series_callback(value: str, ctx: Context):
    """Callback to handle the optical air mass series input or provide a default series."""
    timestamps = ctx.params.get('timestamps')
    optical_air_mass = np.array([OPTICAL_AIR_MASS_DEFAULT for _ in timestamps])
    return OpticalAirMass(value=optical_air_mass, unit=OPTICAL_AIR_MASS_UNIT)


typer_option_optical_air_mass_series = typer.Option(
    help=f'Relative optical air mass series [{OPTICAL_AIR_MASS_UNIT}]',
    parser=parse_optical_air_mass_series,
    callback=optical_air_mass_series_callback,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=OPTICAL_AIR_MASS_DEFAULT,
)
typer_option_apply_atmospheric_refraction = typer.Option(
    help='Apply atmospheric refraction functions',
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
)
typer_option_refracted_solar_zenith = typer.Option(
    help=f'Default refracted solar zenith angle (in radians) for sun -rise and -set events',
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
)
typer_option_albedo = typer.Option(
    min=0,
    help='Mean ground albedo',
    rich_help_panel=rich_help_panel_advanced_options,
    # default_factory = MEAN_GROUND_ALBEDO_DEFAULT,
)

# Solar irradiance
typer_argument_irradiance_series = typer.Argument(
    help='Irradiance series',
    rich_help_panel=rich_help_panel_series_irradiance,
    # default = None,
    show_default=False,
    is_eager=True,
)

global_horizontal_irradiance_typer_help='Global horizontal irradiance (Surface Incoming Shortwave Irradiance (SIS), `ssrd`'
typer_argument_global_horizontal_irradiance = typer.Argument(
    help=global_horizontal_irradiance_typer_help,
    rich_help_panel=rich_help_panel_series_irradiance,
    show_default=False,
)
typer_option_global_horizontal_irradiance = typer.Option(
    # help=global_horizontal_irradiance_typer_help,
    rich_help_panel=rich_help_panel_series_irradiance,
    # default_factory = Path(),
    show_default=False,
)
direct_horizontal_irradiance_typer_help='Direct (or beam) horizontal irradiance (Surface Incoming Direct radiation (SID), `fdir`'
typer_argument_direct_horizontal_irradiance = typer.Argument(
    help=direct_horizontal_irradiance_typer_help,
    rich_help_panel=rich_help_panel_series_irradiance,
    # default_factory=None,
    show_default=False,
)
typer_option_direct_horizontal_irradiance = typer.Option(
    # help=direct_horizontal_irradiance_typer_help,
    rich_help_panel=rich_help_panel_series_irradiance,
    # default_factory = Path(),
    show_default=False,
)
the_term_n_unit='unitless'
typer_argument_term_n = typer.Argument(
    help=f'The term N for the calculation of the sky dome fraction viewed by a tilted surface [{the_term_n_unit}]',
    show_default=False,
)
typer_argument_term_n_series = typer.Argument(
    help=f'The term N for the calculation of the sky dome fraction viewed by a tilted surface for a period of time [{the_term_n_unit}]',
    show_default=False,
    )
typer_option_apply_angular_loss_factor = typer.Option(
    help='Apply angular loss function',
    rich_help_panel=rich_help_panel_advanced_options,
    # default_factory = True,
)
typer_argument_conversion_efficiency = typer.Argument(
    help='Conversion efficiency in %',
    min=0,
    max=100,
    default_factory = None,
    show_default=False,
)
typer_option_system_efficiency = typer.Option(
    '--system-efficiency-factor',
    '-se',
    help='System efficiency factor',
    show_default=True,
    rich_help_panel=rich_help_panel_efficiency,
    # rich_help_panel=rich_help_panel_series_irradiance,
    # default_factory=SYSTEM_EFFICIENCY_DEFAULT,
)
typer_option_efficiency = typer.Option(
    '--efficiency-factor',
    '-e',
    help='PV efficiency factor. [red]Overrides internal PV module efficiency algorithms![/red]',
    rich_help_panel=rich_help_panel_efficiency,
    # rich_help_panel=rich_help_panel_series_irradiance,
    # default_factory=EFFICIENCY_DEFAULT,
)
typer_option_pv_power_algorithm = typer.Option(
    '--power-model',
    '-pm',
    help='Algorithms for calculation of the PV power output of a photovoltaic system as a function of total irradiance and temperature',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_efficiency,
    # default_factory='King'
)
typer_option_module_temperature_algorithm = typer.Option(
    '--temperature-model',
    '-tm',
    help='Algorithms for calculation of the effect of temperature on the power output of a photovoltaic system as a function of temperature and optionally wind speed',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_efficiency,
    # default_factory='Faiman'
)


# Output options

typer_option_verbose = typer.Option(
    '--verbose',
    '-v',
    count=True,
    is_flag=False,
    help='Show details while executing commands',
    rich_help_panel=rich_help_panel_output,
    # default_factory=0,
)
typer_option_index = typer.Option(
    '--index',
    '--idx',
    '-i',
    help="Index rows in output table (works only with at least 1x -v)",
    show_default=True,
    show_choices=True,
    rich_help_panel=rich_help_panel_output,
    # default_factory=False,
)
typer_option_rounding_places = typer.Option(
    '--rounding-places',
    '-r',
    help='Number of digits to round results to',
    show_default=True,
    rich_help_panel=rich_help_panel_output,
    # default_factory=5,
)


# Output units

typer_option_time_output_units = typer.Option(
    '--time-output-units',
    '-tou',
    help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]",
    show_default=True,
    case_sensitive=False,
    # help="Time units for output and internal calculations (seconds, minutes or hours)"
    rich_help_panel=rich_help_panel_output,
)
typer_option_angle_units = typer.Option(
    '--angle-input-units',
    '-aiu',
    help="Angular units for internal solar geometry calculations. :warning: [bold red]Keep fingers away![/bold red]",
    show_default=True,
    case_sensitive=False,
    # help="Angular units for internal calculations (degrees or radians)"
    rich_help_panel=rich_help_panel_output,
)
typer_option_angle_output_units = typer.Option(
    '--angle-ouput-units',
    '-aou',
    help="Angular units for solar geometry calculations (degrees or radians). :warning: [bold red]Under development[/red bold]",
    # help="Angular units for the calculated solar azimuth output (degrees or radians)"
    show_default=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_output,
    # default_factory=ANGLE_OUTPUT_UNITS_DEFAULT,
)
typer_option_statistics = typer.Option(
    help='Calculate and display summary statistics',
    rich_help_panel=rich_help_panel_output,
    # default=False
)
typer_option_groupby = typer.Option(
    help=f"Group statistics, ex. M or 3H. A number and date/time unit : (Y)ear, (M)onth, (D)ay, (W)eek, (S)eason. See Xarray\'s group-by operations.",
    rich_help_panel=rich_help_panel_output,
    # default_factory='h'
)

typer_option_output_filename = typer.Option(
    help='Output filename for the generated figure',
    rich_help_panel=rich_help_panel_output,
    # default=Path(),
)

typer_option_variable_name_as_suffix = typer.Option(
    help='Suffix the output filename with the variable name',
    rich_help_panel=rich_help_panel_output,
    # default=False
)
typer_option_csv = typer.Option(
    help='CSV output filename',
    rich_help_panel=rich_help_panel_output,
    # default_factory='series_in',
)


# Meteorological variables

typer_argument_temperature_time_series = typer.Argument(
    help="Ambient temperature in Celsius degrees.",
    rich_help_panel=rich_help_panel_time_series,
    # default_factory=25,
)
typer_argument_wind_speed_time_series = typer.Argument(
    help="Wind speed in meters per second.",
    rich_help_panel=rich_help_panel_time_series,
    # default_factory=0,
)

# Helpers

typer_option_convert_longitude_360 = typer.Option(
    help='Convert range of longitude values to [0, 360]',
    rich_help_panel="Helpers",
    # default_factory=False
)
typer_option_in_memory = typer.Option(
    help='Use in-memory processing',  # You may need to customize the help text
    # default_factory=False
)

# Plotting

typer_option_uniplot = typer.Option(
    help='Plot the PV power output time series in the terminal',
    rich_help_panel=rich_help_panel_plotting,
    # default_factory=False,
)

typer_option_uniplot_lines = typer.Option(
    help='Symbol for plotting data points with uniplot',
    rich_help_panel=rich_help_panel_plotting,
)
typer_option_uniplot_title = typer.Option(
    help='Title for the Uniplot',
    rich_help_panel=rich_help_panel_plotting,
)
typer_option_uniplot_unit = typer.Option(
    help='Unit for the Uniplot',
    rich_help_panel=rich_help_panel_plotting,
)
typer_option_uniplot_terminal_width = typer.Option(
    help='Fraction of number of columns of the current terminal, ex. 0.9',
    rich_help_panel=rich_help_panel_plotting,
)
typer_option_tufte_style = typer.Option(
    help='Use Tufte-style in the output',  # You may need to customize the help text
    # default_factory=False
)

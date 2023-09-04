import typer
from typer.core import TyperGroup
from click import Context
from typing import Annotated
from typing import Optional
from typing import List
# from typing import Path
from datetime import datetime
from pathlib import Path
from ..api.utilities.conversions import convert_to_radians
from ..api.utilities.timestamp import now_utc_datetimezone
from ..api.utilities.timestamp import ctx_attach_requested_timezone
from ..api.utilities.timestamp import ctx_convert_to_timezone
from ..api.utilities.timestamp import now_local_datetimezone
from ..api.utilities.timestamp import convert_hours_to_datetime_time
from .rich_help_panel_names import rich_help_panel_advanced_options
# from .rich_help_panel_names import rich_help_panel_geometry_time
# from .rich_help_panel_names import rich_help_panel_geometry_position
# from .rich_help_panel_names import rich_help_panel_geometry_refraction
from .rich_help_panel_names import rich_help_panel_geometry_surface
from .rich_help_panel_names import rich_help_panel_solar_position
from .rich_help_panel_names import rich_help_panel_solar_time
from .rich_help_panel_names import rich_help_panel_earth_orbit
from .rich_help_panel_names import rich_help_panel_atmospheric_properties
from .rich_help_panel_names import rich_help_panel_output
from .rich_help_panel_names import rich_help_panel_time_series
from .rich_help_panel_names import rich_help_panel_efficiency
from .rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.api.geometry.models import SolarIncidenceModels
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
# from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import DAYS_IN_A_YEAR
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import LINKE_TURBIDITY_MINIMUM
from pvgisprototype.constants import LINKE_TURBIDITY_MAXIMUM
# from pvgisprototype.constants import LINKE_TURBIDITY_DEFAULT
# from pvgisprototype.constants import OPTICAL_AIR_MASS_DEFAULT
from pvgisprototype.constants import OPTICAL_AIR_MASS_TYPER_UNIT
# from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
# from pvgisprototype.constants import MEAN_GROUND_ALBEDO_DEFAULT
# from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.validation.parameters import BaseTimestampSeriesModel


class OrderCommands(TyperGroup):
  def list_commands(self, ctx: Context):
    """Return list of commands in the order appear.
    See: https://github.com/tiangolo/typer/issues/428#issuecomment-1238866548
    """
    return list(self.commands)


# Generic

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"PVGIS prototype version: {version('pvgis-prototype')}")
        raise typer.Exit(code=0)


typer_option_version = typer.Option(
    "--version",
    help="Show the version of the application and exit",
    callback=_version_callback,
    is_eager=True,
    # default_factory=None,
)


# Where?

longitude_typer_help=f'Longitude in decimal degrees ranging in [-180, 360]. [yellow]If ranging in [0, 360], consider the `--convert-longitude-360` option.[/yellow]'
typer_argument_longitude = typer.Argument(
    min=LONGITUDE_MINIMUM,
    max=LONGITUDE_MAXIMUM,
    help=longitude_typer_help,
    callback=convert_to_radians,
)
typer_argument_longitude_in_degrees = typer.Argument(
    min=LONGITUDE_MINIMUM,
    max=LONGITUDE_MAXIMUM,
    help=longitude_typer_help,
)
latitude_typer_help='Latitude in decimal degrees ranging in [-90, 90]'
typer_argument_latitude = typer.Argument(
    min=LATITUDE_MINIMUM,
    max=LATITUDE_MAXIMUM,
    help=latitude_typer_help,
    callback=convert_to_radians,
)
typer_argument_latitude_in_degrees = typer.Argument(
    min=LATITUDE_MINIMUM,
    max=LATITUDE_MAXIMUM,
    help=latitude_typer_help,
)
typer_argument_elevation = typer.Argument(
    min=ELEVATION_MINIMUM,
    max=ELEVATION_MAXIMUM,
    help='Elevation',
    # rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory=0,
)

# When?

typer_argument_timestamp = typer.Argument(
    help='Timestamp',
    callback=ctx_attach_requested_timezone,
    default_factory=now_utc_datetimezone,
)


def parse_timestamp_series(value: str) -> List[float]:
    datetime_strings = value.split(',')
    datetime_series = [datetime.fromisoformat(string) for string in datetime_strings]
    # return BaseTimestampSeriesModel(timestamps=datetime_series)
    return datetime_series


typer_argument_timestamps = typer.Argument(
    help='Timestamps',
    parser=parse_timestamp_series,
#     default_factory=now_utc_datetimezone_series,
)
typer_option_start_time = typer.Option(
    help='Start timestamp of the period',
    default_factory = None,
)
typer_option_end_time = typer.Option(
    help='End timestamp of the period',
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
# day_of_year: Annotated[float, typer.Argument(
#     min=1,
#     max=366,
#     help='Day of year')] = None,


# Solar geometry

typer_argument_solar_declination = typer.Argument(
    min=SOLAR_DECLINATION_MINIMUM,
    max=SOLAR_DECLINATION_MAXIMUM,
    help='Solar declination angle',
)
typer_option_solar_declination_model = typer.Option(
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    # callback=_parse_model,  # This did not work!
    # help="Model(s) to calculate solar declination."
    help='Model to calculate the solar declination angle',
    # rich_help_panel=rich_help_panel_solar_declination,
    rich_help_panel=rich_help_panel_solar_position,
)

solar_constant_typer_help='Top-of-Atmosphere mean solar electromagnetic radiation (W/m2) 1 au (astronomical unit) away from the Sun.'  #  (~1360.8 W/m2)
typer_argument_solar_constant = typer.Argument(
    min=SOLAR_CONSTANT_MINIMUM,
    help=solar_constant_typer_help,
    rich_help_panel=rich_help_panel_earth_orbit,
    # default_factory = SOLAR_CONSTANT,
)
typer_option_solar_constant = typer.Option(
    min=SOLAR_CONSTANT_MINIMUM,
    help=solar_constant_typer_help,
    rich_help_panel=rich_help_panel_earth_orbit,
    # default_factory = SOLAR_CONSTANT,
)

SOLAR_INCIDENCE_ANGLE_MODEL_DEFAULT=SolarIncidenceModels.jenco
typer_option_solar_incidence_model = typer.Option(
    '--solar-incidence-model',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    help='Method to calculate the solar incidence angle',
    rich_help_panel=rich_help_panel_solar_position,
    # default_factory=SOLAR_INCIDENCE_ANGLE_MODEL_DEFAULT,
)

# Solar surface

surface_tilt_typer_help='Solar surface tilt angle'
typer_argument_surface_tilt = typer.Argument(
    min=SURFACE_TILT_MINIMUM,
    max=SURFACE_TILT_MAXIMUM,
    help=surface_tilt_typer_help,
    callback=convert_to_radians,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_TILT_DEFAULT,
)
typer_option_surface_tilt = typer.Option(
    min=SURFACE_TILT_MINIMUM,
    max=SURFACE_TILT_MAXIMUM,
    help=surface_tilt_typer_help,
    callback=convert_to_radians,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_TILT_DEFAULT,
)
typer_option_random_surface_tilt = typer.Option(
    # min=SURFACE_TILT_MINIMUM,
    # max=SURFACE_TILT_MAXIMUM,
    help='Random solar surface tilt angle',
    # callback=random_surface_tilt,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_TILT_DEFAULT,
)
surface_orientation_typer_help='Solar surface orientation angle. [yellow]Due north is 0 degrees.[/yellow]'
typer_argument_surface_orientation = typer.Argument(
    min=SURFACE_ORIENTATION_MINIMUM,
    max=SURFACE_ORIENTATION_MAXIMUM,
    help=surface_orientation_typer_help,
    callback=convert_to_radians,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_ORIENTATION_DEFAULT,
)
typer_option_surface_orientation = typer.Option(
    min=SURFACE_ORIENTATION_MINIMUM,
    max=SURFACE_ORIENTATION_MAXIMUM,
    help=surface_orientation_typer_help,
    callback=convert_to_radians,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_ORIENTATION_DEFAULT,
)
typer_option_random_surface_orientation = typer.Option(
    # min=SURFACE_ORIENTATION_MINIMUM,
    # max=SURFACE_ORIENTATION_MAXIMUM,
    help='Random solar surface orientation angle. [yellow]Due north is 0 degrees.[/yellow]',
    # callback=random_surface_orientation,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_ORIENTATION_DEFAULT,
)

typer_argument_solar_time = typer.Argument(
    help='The solar time in decimal hours on a 24 hour base',
    callback=convert_hours_to_datetime_time,
    rich_help_panel=rich_help_panel_solar_time,
)
typer_argument_hour_angle = typer.Argument(
    min=0,
    max=1,
    help="Solar hour angle in radians",
    # default_factory=None,
)


# Solar position

typer_option_solar_position_model = typer.Option(
    '--solar-position-model',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    # callback=_parse_model,  # This did not work!
    # help="Model(s) to calculate solar position."
    help='Model to calculate solar position',
    rich_help_panel=rich_help_panel_solar_position,
)

typer_argument_solar_altitude = typer.Argument(
    help='Solar altitude'
)
typer_argument_refracted_solar_altitude = typer.Argument(
    help='Refracted solar altitude'
)


# Solar time

typer_option_solar_time_model = typer.Option(
    '--solar-time-model',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    help="Model to calculate solar time",
    rich_help_panel=rich_help_panel_solar_time,
    # default_factory=[SolarTimeModels.skyfield],
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
    # default_factory=days_in_a_year_default,
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

linke_turbidity_factor_typer_help='Ratio of total to Rayleigh optical depth measuring atmospheric turbidity'
typer_argument_linke_turbidity_factor = typer.Argument(
    min=LINKE_TURBIDITY_MINIMUM,
    max=LINKE_TURBIDITY_MAXIMUM,
    help=linke_turbidity_factor_typer_help,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=LINKE_TURBIDITY_DEFAULT,
)
typer_option_linke_turbidity_factor = typer.Option(
    min=LINKE_TURBIDITY_MINIMUM,
    max=LINKE_TURBIDITY_MAXIMUM,
    help=linke_turbidity_factor_typer_help,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=LINKE_TURBIDITY_DEFAULT,
)


def parse_linke_turbidity_factor_series(value: str) -> BaseTimestampSeriesModel:
    linke_turbidity_factor_strings = value.split(',')
    linke_turbidity_factor_series = [linke_turbidity_factor.fromisoformat(string) for string in linke_turbidity_factor_strings]
    return linke_turbidity_factor_series


linke_turbidity_factor_series_typer_help='Ratio series of total to Rayleigh optical depth measuring atmospheric turbidity'
typer_option_linke_turbidity_factor_series = typer.Option(
    # min=LINKE_TURBIDITY_MINIMUM,
    # max=LINKE_TURBIDITY_MAXIMUM,
    help=linke_turbidity_factor_typer_help,
    parser=parse_linke_turbidity_factor_series,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=LINKE_TURBIDITY_DEFAULT,
)
typer_option_optical_air_mass = typer.Option(
    help=f'Relative optical air mass [{OPTICAL_AIR_MASS_TYPER_UNIT}]',
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=OPTICAL_AIR_MASS_DEFAULT,
)


def parse_optical_air_mass_series(value: str) -> List[float]:
    float_strings = value.split(',')
    return [float(string) for string in float_strings]


typer_option_optical_air_mass_series = typer.Option(
    help=f'Relative optical air mass series [{OPTICAL_AIR_MASS_TYPER_UNIT}]',
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=OPTICAL_AIR_MASS_DEFAULT,
)
typer_option_apply_atmospheric_refraction = typer.Option(
    '--apply-atmospheric-refraction',
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

typer_argument_shortwave_irradiance = typer.Argument(
    help='Global horizontal irradiance (Surface Incoming Shortwave Irradiance (SIS), `ssrd`',
)
typer_argument_direct_horizontal_irradiance = typer.Argument(
    help='Direct (or beam) horizontal irradiance (Surface Incoming Direct radiation (SID), `fdir`',
    rich_help_panel=rich_help_panel_series_irradiance,
    # default_factory=None,
)
typer_option_direct_horizontal_component = typer.Option(
    # help='Path to direct horizontal irradiance time series (Surface Incoming Direct radiation (SID), `fdir`)',
    help='Read horizontal irradiance time series from a file',
    rich_help_panel=rich_help_panel_series_irradiance,
    # default_factory = Path(),
)
the_term_n_unit='unitless'
typer_argument_term_n = typer.Argument(
    help=f'The term N for the calculation of the sky dome fraction viewed by a tilted surface [{the_term_n_unit}]'
)
typer_option_apply_angular_loss_factor = typer.Option(
    help='Apply angular loss function',
    rich_help_panel=rich_help_panel_advanced_options,
    # default_factory = True,
)
typer_option_efficiency = typer.Option(
    '--efficiency-factor',
    '-e',
    help='Efficiency factor',
    rich_help_panel=rich_help_panel_efficiency,
    # rich_help_panel=rich_help_panel_series_irradiance,
    # default_factory=None,
)

# Output options

typer_option_verbose = typer.Option(
    '--verbose',
    '-v',
    # count=True,
    help='Show details while executing commands',
    rich_help_panel=rich_help_panel_output,
    # default_factory=0,
)

typer_option_rounding_places = typer.Option(
    '--rounding-places',
    '-r',
    show_default=True,
    help='Number of digits to round results to',
    rich_help_panel=rich_help_panel_output,
    # default_factory=5,
)


# Output units

typer_option_time_output_units = typer.Option(
    '--time-output-units',
    '-tou',
    show_default=True,
    case_sensitive=False,
    # help="Time units for output and internal calculations (seconds, minutes or hours)"
    help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]",
    rich_help_panel=rich_help_panel_output,
)
typer_option_angle_units = typer.Option(
    '--angle-input-units',
    '-aiu',
    show_default=True,
    case_sensitive=False,
    # help="Angular units for internal calculations (degrees or radians)"
    help="Angular units for internal solar geometry calculations. :warning: [bold red]Keep fingers away![/bold red]",
    rich_help_panel=rich_help_panel_output,
)
typer_option_angle_output_units = typer.Option(
    '--angle-ouput-units',
    '-aou',
    show_default=True,
    case_sensitive=False,
    # help="Angular units for the calculated solar azimuth output (degrees or radians)"
    help="Angular units for solar geometry calculations (degrees or radians). :warning: [bold red]Under development[/red bold]",
    rich_help_panel=rich_help_panel_output,
    # default_factory=ANGLE_OUTPUT_UNITS_DEFAULT,
)
typer_option_statistics = typer.Option(
    help='Calculate and display summary statistics',
    rich_help_panel=rich_help_panel_output,
    # default=False
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


# Time series

typer_argument_time_series = typer.Argument(
    show_default=False,
    help='Input time series data file (any format supported by Xarray)',
    # rich_help_panel=rich_help_panel_time_series,
        )
typer_argument_time = typer.Argument(
    help='Time of data to extract from series. [yellow]Use quotes for a date-time string![/yellow]',
    # rich_help_panel=rich_help_panel_time_series,
    # default_factory=None,
)
typer_option_mask_and_scale = typer.Option(
    help="Mask and scale the series",
    rich_help_panel=rich_help_panel_time_series,
    # default_factory=False,
)
typer_option_inexact_matches_method = typer.Option(
    '--method-for-inexact-matches',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    help="Model to calculate solar position.",
    rich_help_panel=rich_help_panel_time_series,
    # default_factory=MethodsForInexactMatches.nearest,
)
typer_option_tolerance = typer.Option(
    # help=f'Maximum distance between original and new labels for inexact matches. See nearest-neighbor-lookups Xarray documentation',
    # help=f'Maximum distance between original and new labels for inexact matches. See [nearest-neighbor-lookups](https://docs.xarray.dev/en/stable/user-guide/indexing.html#nearest-neighbor-lookups) @ Xarray documentation',
    help=f'Maximum distance between original & new labels for inexact matches. See https://docs.xarray.dev/en/stable/user-guide/indexing.html#nearest-neighbor-lookups',
    rich_help_panel=rich_help_panel_time_series,
    # default_factory=0.1,
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

typer_option_tufte_style = typer.Option(
    help='Use Tufte-style in the output',  # You may need to customize the help text
    # default_factory=False
)

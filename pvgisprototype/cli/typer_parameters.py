import typer
from typing import Annotated
from typing import Optional
# from typing import Path
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


# Generic

typer_option_verbose = typer.Option(
    help='Verbose output',
    rich_help_panel=rich_help_panel_output,
    # default_factory=False,
)


# Where?

typer_argument_longitude = typer.Argument(
    callback=convert_to_radians,
    # min=-180, max=180  # in PVGIS : coloffset
    min=-180, max=360,
    help=f'Longitude in decimal degrees ranging in [-180, 360]. [yellow]Longitude ranging in [0, 360]? Consider using the `--convert-longitude-360` option.[/yellow]',
)
typer_argument_latitude = typer.Argument(
    # min=-90, max=90  # in PVGIS : rowoffset
    help='Latitude in decimal degrees, south is negative',
    callback=convert_to_radians,
)

typer_argument_elevation = typer.Argument(
    min=0, max=8848,
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
typer_option_start_time = typer.Option(
    help='Start date of the period',
    default_factory = None,
)
typer_option_end_time = typer.Option(
    help='End date of the period',
    default_factory = None,
)
typer_option_timezone = typer.Option(
    # help='Timezone (e.g., "Europe/Athens"). Set _local_ to use the system\'s time zone',
    help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
    callback=ctx_convert_to_timezone,
    # default_factory=None,
)
typer_option_local_time = typer.Option(
    help='Use the system\'s local time zone',
    callback=now_local_datetimezone
)
typer_option_random_time = typer.Option(
    '--random-time',
    '--random',
    help="Generate a random date, time and timezone to demonstrate calculation"
)


# Solar geometry

typer_argument_solar_declination = typer.Argument(
    min=0, max=90,
)

typer_argument_solar_constant = typer.Argument(
    min=1360,
    help="Top-of-Atmosphere mean solar electromagnetic radiation, ~1360.8 W/m2, 1 au (astronomical unit) away from the Sun.",
    rich_help_panel=rich_help_panel_earth_orbit,
    # default_factory = SOLAR_CONSTANT,
)

typer_option_solar_incidence_angle_model = typer.Option(
    '--incidence-angle-model',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    help="Method to calculate the solar declination",
    # default_factory= SolarIncidenceAngleMethod.jenco,
)

# Solar surface

typer_argument_surface_tilt = typer.Argument(
    min=0, max=90,
    help='Solar surface tilt angle',
    callback=convert_to_radians,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = 45,
)
typer_option_surface_tilt = typer.Option(
    min=0, max=90,
    help='Solar surface tilt angle',
    callback=convert_to_radians,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = 45,
)

typer_argument_surface_orientation = typer.Argument(
    min=0, max=360,
    help='Solar surface orientation angle. [yellow]Due north is 0 degrees.[/yellow]',
    callback=convert_to_radians,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = 180,  # from North!
)
typer_option_surface_orientation = typer.Option(
    min=0, max=360,
    help='Solar surface orientation angle. [yellow]Due north is 0 degrees.[/yellow]',
    callback=convert_to_radians,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = 180,  # from North!
)

typer_argument_solar_time = typer.Argument(
    help='The solar time in decimal hours on a 24 hour base',
    callback=convert_hours_to_datetime_time,
    rich_help_panel=rich_help_panel_solar_time,
)
typer_argument_hour_angle = typer.Argument(
    min=0, max=1,
    help="Solar hour angle in radians",
    # default_factory=None,
)


# Solar position

typer_option_solar_position_model = typer.Option(
    '--solar-position-model',
    '-m',
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

# Solar time

typer_option_solar_time_model = typer.Option(
    '--solar-time-model',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    help="Model to calculate solar time",
    rich_help_panel=rich_help_panel_solar_time,
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
typer_option_days_in_a_year = typer.Option(
    help='Days in a year',
    rich_help_panel=rich_help_panel_earth_orbit,
    # default_factory=365.25,
)
typer_option_perigee_offset = typer.Option(
    help='Perigee offset',
    rich_help_panel=rich_help_panel_earth_orbit,
    # default_factory=0.048869,
)
typer_option_eccentricity = typer.Option(
    help='Eccentricity',
    rich_help_panel=rich_help_panel_earth_orbit,
    # default_factory=0.01672,
)

typer_option_orbital_eccentricity = typer.Option(0.03344)

help_for_linke_turbidity_factor='Ratio of total to Rayleigh optical depth measuring atmospheric turbidity'
typer_argument_linke_turbidity_factor = typer.Argument(
    help=help_for_linke_turbidity_factor,
    min=0, max=8,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=2,  # 2 to get going for now
)
typer_option_linke_turbidity_factor = typer.Option(
    help=help_for_linke_turbidity_factor,
    min=0, max=8,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=2,  # 2 to get going for now
)

typer_option_apply_atmospheric_refraction = typer.Option(
    '--apply-atmospheric-refraction',
    '-a',
    help='Apply atmospheric refraction functions',
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=True,
)
typer_option_refracted_solar_zenith = typer.Option(
    help=f'Default atmospheric refraction for solar zenith...',
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=1.5853349194640094,  # radians
)

typer_option_albedo = typer.Option(
    min=0,
    help='Mean ground albedo',
    rich_help_panel=rich_help_panel_advanced_options,
    # default_factory = 2,
)

# Solar irradiance

typer_argument_shortwave_irradiance = typer.Argument(
    help='Global horizontal irradiance (Surface Incoming Shortwave Irradiance (SIS), `ssrd`',
)
typer_argument_direct_horizontal_irradiance = typer.Argument(
    help='Direct (or beam) horizontal irradiance (Surface Incoming Direct radiation (SID), `fdir`)',
)
typer_option_direct_horizontal_component = typer.Option(
    help='Read horizontal irradiance time series data from a file',
    # default_factory = Path(),
)

typer_option_apply_angular_loss_factor = typer.Option(
    help='Apply angular loss function',
    rich_help_panel=rich_help_panel_advanced_options,
    # default_factory = True,
)


# Output options

typer_option_rounding_places = typer.Option(
    '--rounding-places',
    '-r',
    show_default=True,
    help='Number of places to round results to.',
    rich_help_panel=rich_help_panel_output,
    # default_factory=5,
)


# Output units

typer_option_time_output_units = typer.Option(
    '--time-output-units',
    '-t',
    show_default=True,
    case_sensitive=False,
    # help="Time units for output and internal calculations (seconds, minutes or hours)"
    help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]",
    rich_help_panel=rich_help_panel_output,
)
typer_option_angle_units = typer.Option(
    '--angle-input-units',
    '-i',
    show_default=True,
    case_sensitive=False,
    # help="Angular units for internal calculations (degrees or radians)"
    help="Angular units for internal solar geometry calculations. :warning: [bold red]Keep fingers away![/bold red]",
    rich_help_panel=rich_help_panel_output,
)
typer_option_angle_output_units = typer.Option(
    '--angle-ouput-units',
    '-u',
    show_default=True,
    case_sensitive=False,
    # help="Angular units for the calculated solar azimuth output (degrees or radians)"
    help="Angular units for solar geometry calculations (degrees or radians). :warning: [bold red]Under development[/red bold]",
    rich_help_panel=rich_help_panel_output,
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
    help=f'Maximum distance between original and new labels for inexact matches. See [nearest-neighbor-lookups](https://docs.xarray.dev/en/stable/user-guide/indexing.html#nearest-neighbor-lookups) @ Xarray documentation',
    rich_help_panel=rich_help_panel_time_series,
    # default_factory=0.1,
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

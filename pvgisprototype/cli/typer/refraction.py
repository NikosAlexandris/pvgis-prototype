import typer
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_atmospheric_properties
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_advanced_options

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

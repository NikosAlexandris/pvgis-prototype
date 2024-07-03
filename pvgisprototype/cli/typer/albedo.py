import typer

from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_advanced_options

typer_option_albedo = typer.Option(
    min=0,
    help="Mean ground albedo",
    rich_help_panel=rich_help_panel_advanced_options,
    # default_factory = MEAN_GROUND_ALBEDO_DEFAULT,
)

import typer
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_solar_position


typer_option_solar_event = typer.Option(
    "--event",
    "--solar-event",
    help="Observable solar event to consider for the surface location and moment or period of the calculations",
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_solar_position,
)

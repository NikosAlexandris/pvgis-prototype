import typer

from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_validation

typer_option_validate_output = typer.Option(
    "--validate-output/--do-not-validate-output",
    help="Validate output range of individual functions.",
    rich_help_panel=rich_help_panel_validation,
    show_default=True,
    show_choices=True,
    case_sensitive=False,
)
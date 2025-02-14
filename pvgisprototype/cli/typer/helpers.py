import typer

# Helpers

typer_option_convert_longitude_360 = typer.Option(
    help="Convert range of longitude values to [0, 360]",
    rich_help_panel="Helpers",
    # default_factory=False
)

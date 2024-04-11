"""
Data processing options
"""


import typer
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_data_processing


typer_option_dtype = typer.Option(
    help=f"Data type",
    rich_help_panel=rich_help_panel_data_processing,
)
typer_option_array_backend = typer.Option(
    help=f"Array backend",
    rich_help_panel=rich_help_panel_data_processing,
)
typer_option_multi_thread = typer.Option(
    help=f"Multi threading",
    rich_help_panel=rich_help_panel_data_processing,
)

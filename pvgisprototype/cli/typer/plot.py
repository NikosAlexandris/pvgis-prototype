"""
Plotting
"""

import typer

from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_plotting

typer_option_uniplot = typer.Option(
    help="Plot the PV power output time series in the terminal",
    rich_help_panel=rich_help_panel_plotting,
    # default_factory=False,
)
typer_option_uniplot_lines = typer.Option(
    help="Symbol for plotting data points with uniplot",
    rich_help_panel=rich_help_panel_plotting,
)
typer_option_uniplot_title = typer.Option(
    help="Title for the Uniplot",
    rich_help_panel=rich_help_panel_plotting,
)
typer_option_uniplot_unit = typer.Option(
    help="Unit for the Uniplot",
    rich_help_panel=rich_help_panel_plotting,
)
typer_option_resample_large_series = typer.Option(
    help="Resample large time series",
    rich_help_panel=rich_help_panel_plotting,
)
typer_option_uniplot_terminal_width = typer.Option(
    help="Fraction of number of columns of the current terminal, ex. 0.9",
    rich_help_panel=rich_help_panel_plotting,
)
typer_option_tufte_style = typer.Option(
    help="Use Tufte-style in the output",  # You may need to customize the help text
    # default_factory=False
)

"""
Statistics related options
"""

import typer

from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_statistics

typer_option_statistics = typer.Option(
    help="Calculate and display summary statistics",
    rich_help_panel=rich_help_panel_statistics,
)
typer_option_groupby = typer.Option(
    help="Group statistics, ex. M or 3h. A number and date/time unit : (Y)ear, (S)eason, (M)onth, (D)ay, (W)eek, (h)our. See Xarray's group-by operations.",
    rich_help_panel=rich_help_panel_statistics,
)
typer_option_analysis = typer.Option(
    help="Analysis of performance. Will force verbose=9 (for detailed calculations) and quiet=True.",
    rich_help_panel=rich_help_panel_statistics,
)
typer_option_nomenclature = typer.Option(
    help="Nomenclature",
    rich_help_panel=rich_help_panel_statistics,
)

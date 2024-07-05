# Solar irradiance

import typer

from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_advanced_options,
    rich_help_panel_irradiance_series,
)

global_horizontal_irradiance_typer_help = (
    "Global horizontal irradiance (Surface Incoming Shortwave Irradiance (SIS), `ssrd`"
)
direct_horizontal_irradiance_typer_help = "Direct (or beam) horizontal irradiance (Surface Incoming Direct radiation (SID), `fdir`"
the_term_n_unit = "unitless"
the_term_n_series_typer_help = (
    f"The term N for the calculation of the sky dome fraction viewed by a tilted surface for a period of time [{the_term_n_unit}]",
)


typer_argument_irradiance_series = typer.Argument(
    help="Irradiance series",
    rich_help_panel=rich_help_panel_irradiance_series,
    show_default=False,
    is_eager=True,
)
typer_argument_global_horizontal_irradiance = typer.Argument(
    help=global_horizontal_irradiance_typer_help,
    rich_help_panel=rich_help_panel_irradiance_series,
    show_default=False,
)
typer_option_global_horizontal_irradiance = typer.Option(
    help=global_horizontal_irradiance_typer_help,
    rich_help_panel=rich_help_panel_irradiance_series,
    show_default=False,
)
typer_argument_direct_horizontal_irradiance = typer.Argument(
    help=direct_horizontal_irradiance_typer_help,
    rich_help_panel=rich_help_panel_irradiance_series,
    show_default=False,
)
typer_option_direct_horizontal_irradiance = typer.Option(
    help=direct_horizontal_irradiance_typer_help,
    rich_help_panel=rich_help_panel_irradiance_series,
    show_default=False,
)
typer_argument_term_n = typer.Argument(
    help=the_term_n_series_typer_help,
    show_default=False,
)
typer_argument_term_n_series = typer.Argument(
    help=the_term_n_series_typer_help,
    show_default=False,
)
typer_option_apply_reflectivity_factor = typer.Option(
    help="Apply angular loss function",
    rich_help_panel=rich_help_panel_advanced_options,
)

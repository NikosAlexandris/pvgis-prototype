import typer
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_surface_position,
)

typer_option_surface_position_optimiser_mode = typer.Option(
    "--surface-position-optimiser-mode",
    "--optimiser-mode",
    help="Mode for which to optimise the positioning angle",
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    # callback=_parse_model,  # This did not work!
    rich_help_panel=rich_help_panel_surface_position,
)
typer_option_precision_goal_for_surface_position_optimiser = typer.Option(
    "--optimiser-precision-goal",
    "--precision-goal",
    help="Precision goal for the optimiser of the position of a solar surface",
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    # callback=_parse_methodl,  # This did not work!
    rich_help_panel=rich_help_panel_surface_position,
)
typer_option_surface_position_optimiser_method = typer.Option(
    "--surface-position-optimiser",
    "--optimiser",
    help="Method to optimise the positioning of a solar surface",
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    # callback=_parse_methodl,  # This did not work!
    rich_help_panel=rich_help_panel_surface_position,
)
typer_option_number_of_iterations_for_surface_position_optimiser = typer.Option(
    "--iterations",
    "--optimiser-iterations",
    help="Number of iterations to optimise the positioning of a solar surface",
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    # callback=_parse_methodl,  # This did not work!
    rich_help_panel=rich_help_panel_surface_position,
)
typer_option_surface_position_optimiser_shgo_sampling_method = typer.Option(
    "--shgo-sampling-method",
    "--shgo-sampling-method",
    help="Sampling method for the SHGO optimiser of the position of a solar surface",
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    # callback=_parse_sampling_methodl,  # This did not work!
    rich_help_panel=rich_help_panel_surface_position,
)
typer_option_number_of_sampling_points_for_surface_position_optimiser = typer.Option(
    "--sampling-points",
    "--optimiser-sampling-points",
    help="Number of sampling points for the optimiser of the position of a solar surface",
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    # callback=_parse_methodl,  # This did not work!
    rich_help_panel=rich_help_panel_surface_position,
)

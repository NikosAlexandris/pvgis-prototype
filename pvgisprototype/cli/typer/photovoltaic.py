"""
Generic input and output function parameters 
"""

import typer
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_efficiency


typer_argument_pv_technology = typer.Argument(
    help='Technology of the PV module: crystalline silicon cells, thin film modules made from CIS or CIGS, thin film modules made from Cadmium Telluride (CdTe), other/unknown',
    show_default=False,
)
typer_argument_mounting_type = typer.Argument(
    help='Type of mounting',  # in PVGIS : mountingplace
    # default_factory = 'free',  # see PVGIS for more!
    show_default=False,
)
typer_argument_area = typer.Argument(
    help='The area of the modules in m<sup>2</sup>',
    min=0.001,  # min of mini-solar-panel?
    # rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = None,
    show_default=False,
)

typer_option_photovoltaic_module_model = typer.Option(
    '--photovoltaic-module',
    help='Technology and type of the photovoltaic module',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    # callback=_parse_model,  # This did not work!
    rich_help_panel=rich_help_panel_efficiency,
)

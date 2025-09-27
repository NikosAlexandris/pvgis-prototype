#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
"""
Generic input and output function parameters
"""

import typer
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_efficiency

typer_option_photovoltaic_module_type = typer.Option(
    help="Photovoltaic module type",
    show_default=True,
    rich_help_panel=rich_help_panel_efficiency,
)
typer_argument_pv_technology = typer.Argument(
    help="Technology of the PV module: crystalline silicon cells, thin film modules made from CIS or CIGS, thin film modules made from Cadmium Telluride (CdTe), other/unknown",
    show_default=False,
    rich_help_panel=rich_help_panel_efficiency,
)
typer_option_photovoltaic_module_peak_power = typer.Option(
    help="The declared power in kilowatt-peak (kWp) the module can produce under standard test conditions (1000 W/m<sup>2</sup> of in-plane solar irradiance, at 25°C of module temperature.",
    show_default=True,
    rich_help_panel=rich_help_panel_efficiency,
)
typer_option_photovoltaic_module_conversion_efficiency = typer.Option(
    help="The declared conversion efficiency (in percent)",
    show_default=False,
    rich_help_panel=rich_help_panel_efficiency,
)
typer_argument_mounting_type = typer.Argument(
    help="Type of mounting",  # in PVGIS : mountingplace
    # default_factory = 'free',  # see PVGIS for more!
    show_default=False,
    rich_help_panel=rich_help_panel_efficiency,
)
typer_argument_area = typer.Argument(
    help="The area of the modules in m<sup>2</sup>",
    min=0.001,  # min of mini-solar-panel?
    # rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = None,
    show_default=False,
    rich_help_panel=rich_help_panel_efficiency,
)
typer_option_photovoltaic_module_model = typer.Option(
    "--photovoltaic-module",
    help="Technology and type of the photovoltaic module",
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    # callback=_parse_model,  # This did not work!
    rich_help_panel=rich_help_panel_efficiency,
)

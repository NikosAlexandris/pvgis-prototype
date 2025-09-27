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
import typer

from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_efficiency

typer_argument_conversion_efficiency = typer.Argument(
    help="Conversion efficiency in %",
    min=0,
    max=100,
    default_factory=None,
    show_default=False,
)
typer_option_system_efficiency = typer.Option(
    "--system-efficiency-factor",
    "-se",
    help="System efficiency factor",
    show_default=True,
    rich_help_panel=rich_help_panel_efficiency,
    # rich_help_panel=rich_help_panel_series_irradiance,
    # default_factory=SYSTEM_EFFICIENCY_DEFAULT,
)
typer_option_efficiency = typer.Option(
    "--efficiency-factor",
    "-e",
    help="PV efficiency factor. [red]Overrides internal PV module efficiency algorithms![/red]",
    rich_help_panel=rich_help_panel_efficiency,
    # rich_help_panel=rich_help_panel_series_irradiance,
    # default_factory=EFFICIENCY_DEFAULT,
)
typer_option_pv_power_algorithm = typer.Option(
    "--power-model",
    "-pm",
    help="Algorithms for calculation of the PV power output of a photovoltaic system as a function of total irradiance and temperature",
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_efficiency,
    # default_factory='King'
)
typer_option_module_temperature_algorithm = typer.Option(
    "--temperature-model",
    "-tm",
    help="Algorithms for calculation of the effect of temperature on the power output of a photovoltaic system as a function of temperature and optionally wind speed",
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_efficiency,
    # default_factory='Faiman'
)

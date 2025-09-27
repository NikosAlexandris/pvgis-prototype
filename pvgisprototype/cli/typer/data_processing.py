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
Data processing options
"""

import typer

from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_data_processing

typer_option_dtype = typer.Option(
    help="Data type",
    rich_help_panel=rich_help_panel_data_processing,
)
typer_option_array_backend = typer.Option(
    help="Array backend",
    rich_help_panel=rich_help_panel_data_processing,
)
typer_option_multi_thread = typer.Option(
    help="Multi threading",
    rich_help_panel=rich_help_panel_data_processing,
)

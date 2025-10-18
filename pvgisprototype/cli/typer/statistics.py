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
    # see also : `typer_option_verbosity` in verosity.py
    help="Analysis of performance. Will force verbose=9 (for detailed calculations) and quiet=True.",
    rich_help_panel=rich_help_panel_statistics,
)
typer_option_nomenclature = typer.Option(
    help="Nomenclature",
    rich_help_panel=rich_help_panel_statistics,
)

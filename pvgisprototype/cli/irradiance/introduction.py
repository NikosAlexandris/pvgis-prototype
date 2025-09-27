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
from pvgisprototype.documentation.irradiance import A_PRIMER_ON_SOLAR_IRRADIANCE


def solar_irradiance_introduction():
    """A short introduction on solar irradiance"""
    introduction = """
    [underline]Solar irradiance[/underline] is ...
    """
    note = """
    PVGIS can model solar irradiance components or read selectively
    [magenta]global[/magenta] or [magenta]direct[/magenta] irradiance time series from external datasets.
    """
    from rich.panel import Panel

    note_in_a_panel = Panel(
        "[italic]{}[/italic]".format(note),
        title="[bold cyan]Note[/bold cyan]",
        width=78,
    )
    from rich.console import Console

    console = Console()
    # introduction.wrap(console, 30)
    console.print(introduction)
    console.print(note_in_a_panel)
    console.print(A_PRIMER_ON_SOLAR_IRRADIANCE)

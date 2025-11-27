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
from pvgisprototype.documentation.tmy import A_PRIMER_ON_TYPICAL_METEOROLOGICAL_YEAR


def introduction():
    """
    A short introduction on the Typical Meteorological Year
    """
    introduction = """The [underline]Typical Meteorological Year[/underline]
    (TMY) is a dataset designed to represent the most _typical_ weather
    conditions for each month at a given location, using historical data. This
    dataset is particularly useful for simulations in solar energy and building
    performance."""
    note = """Internally, [bold]timestamps[/bold] are converted to
    [magenta]UTC[/magenta] and [bold]angles[/bold] are measured in
    [magenta]radians[/magenta] !
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
    console.print(A_PRIMER_ON_TYPICAL_METEOROLOGICAL_YEAR)

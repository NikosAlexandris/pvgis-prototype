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
def series_introduction():
    """A short introduction on the series command"""
    introduction = """
    The [code]series[/code] command is a convenience wrapper around Xarray's
    data processing capabilities.

    Explain [bold cyan]timestamps[/bold cyan].

    And more ...

    """

    note = """
    Timestamps are retrieved from the input data series. If the series are not
    timestamped, then stamps are generated based on the user requested
    combination of a three out of the four relevant parameters : `start-time`,
    `end-time`, `frequency` and `period`.

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

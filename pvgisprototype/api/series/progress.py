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
from contextlib import nullcontext
from enum import Enum

from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn


class DisplayMode(Enum):
    SILENT = 0
    SPINNER = 1
    BARS = 2


console = Console()
display_context = {
    DisplayMode.SILENT: nullcontext(),
    DisplayMode.SPINNER: console.status("[bold green]Processing..."),
    DisplayMode.BARS: Progress(transient=True),
}


progress = Progress(
    TextColumn("[bold blue]{task.description}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    TimeRemainingColumn(),
)

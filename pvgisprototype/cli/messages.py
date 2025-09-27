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
from pvgisprototype.api.series.hardcodings import x_mark

NOT_COMPLETE = "[orange]Not complete. [bold]Yet![/bold][/orange]"
NOT_COMPLETE_CLI = "[bold yellow]Yet not complete![/bold yellow]"
NOT_IMPLEMENTED = "[red]Not implemented. [bold]Yet![/bold][/red]"
NOT_IMPLEMENTED_CLI = "[bold red]Yet not implemented![/bold red]"
TO_MERGE_WITH_SINGLE_VALUE_COMMAND = "[cyan]To merge with single-value command[/cyan]"
WARNING_NEGATIVE_VALUES = "[bold black on red] Warning [/bold black on red] : I found some [red bold]negative value/s[/red bold]"
WARNING_OUT_OF_RANGE_VALUES = "[black on yellow]I found some value/s out of the expected range[/black on yellow]"
ERROR_IN_SELECTING_DATA = f"[red blink]{x_mark}[/red blink] [red on white]Something went wrong in [bold]selecting[/bold] the data[/red on white]"
ERROR_IN_PLOTTING_DATA = f"[red blink]{x_mark}[/red blink] [red on white]Something went wrong in [bold]plotting[/bold] the data[/red on white]"

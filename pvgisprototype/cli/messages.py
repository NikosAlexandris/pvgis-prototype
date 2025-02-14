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

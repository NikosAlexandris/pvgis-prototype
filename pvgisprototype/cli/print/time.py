from rich.panel import Panel
from rich.table import Table


def build_time_table() -> Table:
    """ """
    time_table = Table(
        box=None,
        show_header=True,
        header_style=None,
        show_edge=False,
        pad_edge=False,
    )
    time_table.add_column("Start", justify="left", style="bold")
    time_table.add_column("Every", justify="left", style="dim bold")
    time_table.add_column("End", justify="left", style="dim bold")
    time_table.add_column("Zone", justify="left", style="dim bold")

    return time_table


def build_time_panel(
    time_table,
    safe_box: bool = True,
    expand: bool = False,
    padding: tuple = (0, 2),
) -> Panel:
    """ """
    return Panel(
        time_table,
        # title="Time",
        # subtitle="Time",
        # subtitle_align="right",
        safe_box=safe_box,
        border_style="dim",
        expand=expand,
        padding=padding,
    )

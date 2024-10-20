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

from pvgisprototype.documentation.photovoltaics import A_PRIMER_ON_PHOTOVOLTAIC_PERFORMANCE


def photovoltaic_performance_introduction():
    """A short introduction on photovoltaic performance"""
    introduction = """
    [underline]The performance of a photovoltaic (PV) system[/underline] is ...
    """
    note = """
    PVGIS can estimate the performance of a series of photovoltaic technologies using either [magenta]broadband[/magenta] or [magenta]spectrally resolved[/magenta] irradiance data.
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
    console.print(A_PRIMER_ON_PHOTOVOLTAIC_PERFORMANCE)

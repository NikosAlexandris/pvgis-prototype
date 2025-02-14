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

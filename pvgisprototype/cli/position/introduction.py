from pvgisprototype.documentation.solar_geometry import A_PRIMER_ON_SOLAR_GEOMETRY


def introduction():
    """A short introduction on solar position"""
    introduction = """
    [underline]Solar position[/underline] consists of a series of angular
    measurements between the position of the sun in the sky and a location on
    the surface of the earth for a moment or a period in time.
    """

    note = """Internally, [bold]timestamps[/bold] are converted to [magenta]UTC[/magenta] and [bold]angles[/bold] are measured in [magenta]radians[/magenta] !
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
    console.print(A_PRIMER_ON_SOLAR_GEOMETRY)

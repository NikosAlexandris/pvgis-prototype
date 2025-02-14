from pvgisprototype.documentation.tmy import A_PRIMER_ON_TYPICAL_METEOROLOGICAL_YEAR


def introduction():
    """A short introduction on the Typical Meteorological Year"""
    introduction = """ The [underline]Typical Meteorological Year[/underline] (TMY) is a dataset
    designed to represent the most _typical_ weather conditions for each month
    at a given location, using historical data. This dataset is particularly
    useful for simulations in solar energy and building performance.
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
    console.print(A_PRIMER_ON_TYPICAL_METEOROLOGICAL_YEAR)

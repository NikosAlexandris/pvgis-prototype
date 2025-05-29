from rich.table import Table
from rich.panel import Panel
from pvgisprototype.cli.plot.uniplot import Plot
from pvgisprototype.constants import HORIZON_HEIGHT_NAME
from rich.box import MINIMAL


def build_horizon_profile_table() -> Table:
    """ """
    horizon_profile_table = Table(
        box=None,
        show_header=True,
        header_style="bold dim",
        show_edge=False,
        pad_edge=False,
    )
    horizon_profile_table.add_column(
        f"{HORIZON_HEIGHT_NAME}",
        # justify="right",
        style="bold", no_wrap=True
    )

    return horizon_profile_table


def generate_horizon_profile_polar_plot(
        horizon_profile,
        ) -> Plot:
    """
    """
    azimuthal_directions_radians = numpy.linspace(0, 2 * numpy.pi, horizon_profile.size)
    from pvgisprototype.cli.plot.uniplot import Plot
    horizon_profile_polar_plot = Plot(
        xs=numpy.degrees(azimuthal_directions_radians),
        ys=horizon_profile,
        lines=True,
        width=45,
        height=3,
        x_gridlines=[],
        y_gridlines=[],
        character_set="braille",
        # color=[colors[1]],
        # legend_labels=[labels[1]],
        color=["blue"],  # Add color
        legend_labels=["Horizon Profile"],  # Add legend
        interactive=False,
    )

    return horizon_profile_polar_plot


def build_horizon_profile_panel(horizon_profile_table) -> Panel:
    """ """
    return Panel(
        horizon_profile_table,
        # subtitle="Horizon height profile",
        # subtitle_align="right",
        box=MINIMAL,
        # safe_box=True,
        # border_style=None,
        # style="",
        expand=False,
        padding=0,
        width=60,
    )

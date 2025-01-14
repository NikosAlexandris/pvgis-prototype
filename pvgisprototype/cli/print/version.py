from rich.console import JustifyMethod
from rich.panel import Panel
from rich.text import Text


def build_pvgis_version_panel(
    prefix_text: str = "PVGIS v6",
    justify_text: JustifyMethod = "center",
    style_text: str = "white dim",
    border_style: str = "dim",
    padding: tuple = (0, 2),
) -> Panel:
    """ """
    from pvgisprototype._version import __version__

    pvgis_version = Text(
        f"{prefix_text} ({__version__})",
        justify=justify_text,
        style=style_text,
    )
    return Panel(
        pvgis_version,
        # subtitle="[reverse]Fingerprint[/reverse]",
        # subtitle_align="right",
        border_style=border_style,
        # style="dim",
        expand=False,
        padding=padding,
    )

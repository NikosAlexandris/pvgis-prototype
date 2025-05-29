from pvgisprototype.constants import FINGERPRINT_COLUMN_NAME
from rich.panel import Panel
from rich.text import Text
from rich.console import Console


def retrieve_fingerprint(
    dictionary: dict, fingerprint_key: str = FINGERPRINT_COLUMN_NAME
) -> str | None:
    """Recursively search for the fingerprint key in a nested dictionary."""
    if isinstance(dictionary, dict):
        if fingerprint_key in dictionary:
            return dictionary[fingerprint_key]

        # Recursively search each value of the dictionary
        for _, value in dictionary.items():
            fingerprint = retrieve_fingerprint(value)
            if fingerprint is not None:
                return fingerprint

    return None


def print_finger_hash(
    dictionary: dict,
    fingerprint_key: str = FINGERPRINT_COLUMN_NAME,
):
    """Print the fingerprint if found, otherwise print a warning."""
    fingerprint = retrieve_fingerprint(
            dictionary,
            fingerprint_key,
            )
    if fingerprint is None:
        fingerprint = "No fingerprint found!"
        color = "red"
    else:
        color = "yellow"

    fingerprint_panel = Panel.fit(
        Text(f"{fingerprint}", justify="center", style=f"bold {color}"),
        subtitle="[reverse]Fingerprint[/reverse]",
        subtitle_align="right",
        border_style="dim",
        style="dim",
    )
    Console().print(fingerprint_panel)


def build_fingerprint_panel(fingerprint) -> Panel:
    """ """
    fingerprint = Text(
        fingerprint,
        justify="center",
        style="yellow bold",
    )
    return Panel(
        fingerprint,
        subtitle="[reverse]Fingerprint[/reverse]",
        subtitle_align="right",
        border_style="dim",
        style="dim",
        expand=False,
        padding=(0, 2),
    )

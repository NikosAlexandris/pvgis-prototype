from rich.columns import Columns
from rich.panel import Panel
from pvgisprototype.cli.print.version import build_pvgis_version_panel
from pvgisprototype.cli.print.fingerprint import build_fingerprint_panel


def build_version_and_fingerprint_panels(
    version:bool = False,
    fingerprint: bool = False,
) -> list[Panel]:
    """Dynamically build panels based on available data."""
    # Always yield version panel
    panels = []
    if version:
        panels.append(build_pvgis_version_panel())
    # Yield fingerprint panel only if fingerprint is provided
    if fingerprint:
        panels.append(build_fingerprint_panel(fingerprint))

    return panels


def build_version_and_fingerprint_columns(
    version:bool = False,
    fingerprint: bool = False,
) -> Columns:
    """Combine software version and fingerprint panels into a single Columns
    object."""
    version_and_fingeprint_panels = build_version_and_fingerprint_panels(
        version=version,
        fingerprint=fingerprint,
    )

    return Columns(version_and_fingeprint_panels, expand=False, padding=2)

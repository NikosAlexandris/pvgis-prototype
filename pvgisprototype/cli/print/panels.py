#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
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

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

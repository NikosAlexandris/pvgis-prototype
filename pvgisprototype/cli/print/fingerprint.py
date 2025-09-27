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
from pvgisprototype.constants import FINGERPRINT_COLUMN_NAME
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from pvgisprototype.log import logger


def retrieve_fingerprint(
    dictionary: dict, fingerprint_key: str = FINGERPRINT_COLUMN_NAME
) -> str | None:
    """
    Recursively search for the fingerprint key in a nested dictionary.
    """
    if isinstance(dictionary, dict):
        if fingerprint_key in dictionary:
            logger.info(f"Found the fingerprint key {fingerprint_key=}")
            return dictionary[fingerprint_key]

        # Recursively search each value of the dictionary
        for _, value in dictionary.items():
            fingerprint = retrieve_fingerprint(value)
            if fingerprint is not None:
                logger.info(f"Retrieved the fingerprint {fingerprint=}")
                return fingerprint

    logger.debug(f"Did not identify a fingerprint in the input data structure {dictionary=} !")
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

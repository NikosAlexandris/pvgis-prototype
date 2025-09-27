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
from pvgisprototype import PhotovoltaicPower
from rich.table import Table
from rich.panel import Panel
from pvgisprototype.constants import (
    AZIMUTH_ORIGIN_NAME,
    INCIDENCE_DEFINITION,
    POSITIONING_ALGORITHM_NAME,
    SHADING_ALGORITHM_NAME,
    TIMING_ALGORITHM_NAME,
)


def build_algorithmic_metadata_table() -> Table:
    """ """
    algorithmic_metadata_table = Table(
        box=None,
        show_header=True,
        header_style="bold dim",
        show_edge=False,
        pad_edge=False,
    )
    algorithmic_metadata_table.add_column(
        f"{TIMING_ALGORITHM_NAME}", justify="center", style="bold", no_wrap=True
    )
    algorithmic_metadata_table.add_column(
        f"{POSITIONING_ALGORITHM_NAME}", justify="center", style="bold", no_wrap=True
    )
    # algorithmic_metadata_table.add_column(
    #     # f"{INCIDENCE_ALGORITHM_NAME}", justify="center", style="bold", no_wrap=True
    #     f"{INCIDENCE_NAME}", justify="center", style="bold", no_wrap=True
    # )
    algorithmic_metadata_table.add_column(
        f"{AZIMUTH_ORIGIN_NAME}", justify="center", style="bold", no_wrap=True
    )
    algorithmic_metadata_table.add_column(
        f"{INCIDENCE_DEFINITION}", justify="center", style="bold", no_wrap=True
    )
    algorithmic_metadata_table.add_column(
        f"{SHADING_ALGORITHM_NAME}", justify="center", style="bold", no_wrap=True
    )
    # algorithmic_metadata_table.add_column(
    #     f"{HORIZON_HEIGHT_NAME}", justify="center", style="bold", no_wrap=True
    # )

    return algorithmic_metadata_table


def populate_algorithmic_metadata_table(
        data_model: PhotovoltaicPower,
        ) -> Table | None:
    """
    """
    timing_algorithm = data_model.solar_timing_algorithm
    positioning_algorithm = data_model.solar_positioning_algorithm
    azimuth_origin = data_model.azimuth_origin
    incidence_angle_definition = data_model.solar_incidence_definition
    incidence_algorithm = data_model.solar_incidence_model
    shading_algorithm = data_model.shading_algorithm
    if all(
        [
        timing_algorithm,
        positioning_algorithm,
        azimuth_origin,
        incidence_angle_definition,
        incidence_algorithm,
        ]
    ):
        algorithmic_metadata_table = build_algorithmic_metadata_table()
        algorithmic_metadata_table.add_row(
            f"{timing_algorithm}",
            f"{positioning_algorithm}",
            # f"{incidence_algorithm}",
            f"{azimuth_origin}",
            f"{incidence_angle_definition}, {incidence_algorithm}",
            f"{shading_algorithm}",
        )
        return algorithmic_metadata_table

    else:
        return None


def build_algorithmic_metadata_panel(algorithmic_metadata_table) -> Panel | None:
    """ """
    if algorithmic_metadata_table is None:
        return None

    else:
        return Panel(
            algorithmic_metadata_table,
            subtitle="Algorithmic metadata",
            subtitle_align="right",
            # box=None,
            safe_box=True,
            style="",
            expand=False,
            padding=(0, 3),
        )

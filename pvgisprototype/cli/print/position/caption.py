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
from zoneinfo import ZoneInfo
from pvgisprototype.cli.print.getters import get_value_or_default
from pvgisprototype.constants import (
    AZIMUTH_ORIGIN_NAME,
    ECCENTRICITY_AMPLITUDE_COLUMN_NAME,
    ECCENTRICITY_PHASE_OFFSET_COLUMN_NAME,
    ECCENTRICITY_PHASE_OFFSET_SHORT_COLUMN_NAME,
    INCIDENCE_ALGORITHM_COLUMN_NAME,
    INCIDENCE_DEFINITION,
    INCIDENCE_DEFINITION_COLUMN_NAME,
    POSITIONING_ALGORITHM_COLUMN_NAME,
    SHADING_ALGORITHM_NAME,
    SHADING_STATES_COLUMN_NAME,
    SOLAR_CONSTANT_COLUMN_NAME,
    TIME_ALGORITHM_COLUMN_NAME,
    SOLAR_POSITIONS_TO_HORIZON_COLUMN_NAME,
)
def build_solar_position_model_caption(
    solar_position_model,
    main_caption,
    timezone,
    surface_orientation=True,
    surface_tilt=True,
):
    """
    """
    # print(f"{solar_position_model=}\n\n")
    # print(f"{solar_position_model.keys()=}")
    model_caption = main_caption

    # solar_positioning_algorithm = get_value_or_default(
    solar_positioning_algorithm = solar_position_model.get(
        # solar_position_model, POSITIONING_ALGORITHM_NAME, None
        POSITIONING_ALGORITHM_COLUMN_NAME, None
    )
    if solar_position_model.get(SOLAR_POSITIONS_TO_HORIZON_COLUMN_NAME) is not None:
        solar_positions_to_horizon = [position.value for position in solar_position_model.get(SOLAR_POSITIONS_TO_HORIZON_COLUMN_NAME, None)]
    else:
        solar_positions_to_horizon = None

    incidence_algorithm = solar_position_model.get(
            # solar_position_model, INCIDENCE_ALGORITHM_NAME, None
            INCIDENCE_ALGORITHM_COLUMN_NAME, None
        )

    shading_algorithm = get_value_or_default(
        solar_position_model, SHADING_ALGORITHM_NAME, None
    )

    # if solar_position_model.get(SHADING_STATES_COLUMN_NAME) is not None:
    #     shading_states = [state.value for state in solar_position_model.get(SHADING_STATES_COLUMN_NAME, None)]
    # else:
    #     shading_states = None

    # ----------------------------------------------------------------
    if surface_orientation or surface_tilt:
        model_caption += "\n[underline]Definitions[/underline]  "

    azimuth_origin = get_value_or_default(
        solar_position_model, AZIMUTH_ORIGIN_NAME, None
    )
    if azimuth_origin:
        model_caption += (
            f"Azimuth origin : [bold green]{azimuth_origin}[/bold green], "
        )

    # Fundamental Definitions

    if timezone:
        if timezone == ZoneInfo('UTC'):
            model_caption += f"[bold]{timezone}[/bold], "
        else:
            model_caption += f"Local Zone : [bold]{timezone}[/bold], "


    if incidence_algorithm:
        solar_incidence_definition = solar_position_model.get(INCIDENCE_DEFINITION_COLUMN_NAME, None)
        if solar_incidence_definition is not None:
            model_caption += f"{INCIDENCE_DEFINITION}: [bold yellow]{solar_incidence_definition}[/bold yellow]"

    solar_constant = solar_position_model.get(SOLAR_CONSTANT_COLUMN_NAME, None)
    eccentricity_phase_offset = solar_position_model.get(ECCENTRICITY_PHASE_OFFSET_COLUMN_NAME, None)
    eccentricity_amplitude = solar_position_model.get(
        ECCENTRICITY_AMPLITUDE_COLUMN_NAME, None
    )

    if solar_positions_to_horizon:
        model_caption += f"Positions to horizon : [bold]{solar_positions_to_horizon}[/bold], "

    # Algorithms

    # if algorithms or timing_algorithm or solar_positioning_algorithm:
    #     model_caption += "\n[underline]Algorithms[/underline]  "

    timing_algorithm = solar_position_model.get(TIME_ALGORITHM_COLUMN_NAME, None)
    if timing_algorithm:
        model_caption += f"Timing : [bold]{timing_algorithm}[/bold], "

    if solar_positioning_algorithm:
        model_caption += f"Positioning : [bold]{solar_positioning_algorithm}[/bold], "

    adjusted_for_atmospheric_refraction = solar_position_model.get('Unrefracted ⦧', None)
    if adjusted_for_atmospheric_refraction:
        # caption += f"\n[underline]Atmospheric Properties[/underline]  "
        model_caption += f"Adjusted for refraction : [bold]{adjusted_for_atmospheric_refraction}[/bold], "

    if incidence_algorithm:
        model_caption += f"Incidence : [bold yellow]{incidence_algorithm}[/bold yellow], "

    if shading_algorithm:
        model_caption += f"Shading : [bold]{shading_algorithm}[/bold]"

    # if shading_states:
    #     model_caption += f"Shading states : [bold]{shading_states}[/bold]"


    if any([solar_constant, eccentricity_phase_offset, eccentricity_amplitude]):
        model_caption += "\n[underline]Constants[/underline] "
        if solar_constant:
            model_caption += f"{SOLAR_CONSTANT_COLUMN_NAME} : {solar_constant}, "

        if eccentricity_phase_offset and eccentricity_amplitude:
            model_caption += f"{ECCENTRICITY_PHASE_OFFSET_SHORT_COLUMN_NAME} : {eccentricity_phase_offset}, "
            model_caption += f"{ECCENTRICITY_AMPLITUDE_COLUMN_NAME} : {eccentricity_amplitude}, "

    return model_caption.rstrip(", ")  # Remove trailing comma + space

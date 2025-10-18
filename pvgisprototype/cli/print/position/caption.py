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
from pvgisprototype.api.position.models import SolarPositionParameterColumnName, SolarPositionParameterMetadataColumnName
from pvgisprototype.cli.print.getters import get_value_or_default
from pvgisprototype.constants import (
    ECCENTRICITY_AMPLITUDE_COLUMN_NAME,
    ECCENTRICITY_PHASE_OFFSET_COLUMN_NAME,
    ECCENTRICITY_PHASE_OFFSET_SHORT_COLUMN_NAME,
)


def build_solar_position_model_caption(
    solar_position_model_data,
    caption,
    timezone,
    user_requested_timezone,
    surface_orientation=True,
    surface_tilt=True,
):
    """
    """
    # Definitions
    ## Azimuth origin : North
    azimuth_origin = solar_position_model_data.get(SolarPositionParameterMetadataColumnName.azimuth_origin, None)
    ## Timezone or UTC

    ## Positions sun-to-horizon : from the set {['Above', 'Low angle', 'Below']}
    ## for which calculations were performed !
    if solar_position_model_data.get(SolarPositionParameterMetadataColumnName.sun_horizon_positions, None):
        sun_horizon_positions = [position.value for position in solar_position_model_data.get(SolarPositionParameterMetadataColumnName.sun_horizon_positions, None)]
    else:
        sun_horizon_positions = None

    # Algorithms
    ## Timing : e.g. NOAA
    timing_algorithm = solar_position_model_data.get(SolarPositionParameterColumnName.timing, None)

    ## Positioning : e.g. NOAA
    # solar_positioning_algorithm = get_value_or_default(
    solar_positioning_algorithm = solar_position_model_data.get(
        # solar_position_model, POSITIONING_ALGORITHM_NAME, None
        SolarPositionParameterColumnName.positioning, None
    )
    adjusted_for_atmospheric_refraction = solar_position_model_data.get('Unrefracted ⌮', None)

    ## Incidence : e.g. Iqbal
    incidence_algorithm = solar_position_model_data.get(
            # solar_position_model, INCIDENCE_ALGORITHM_NAME, None
            SolarPositionParameterMetadataColumnName.incidence_algorithm, None
        )
    ## Incidence angle : e.g. Sun-Vector-to-Surface-Plane
    solar_incidence_definition = None
    if incidence_algorithm:
        solar_incidence_definition = solar_position_model_data.get(SolarPositionParameterMetadataColumnName.incidence_definition, None)
    
    ## Shading : e.g. PVGIS
    shading_algorithm = get_value_or_default(
        solar_position_model_data, SolarPositionParameterMetadataColumnName.shading_algorithm, None
    )

    ## Shading states : ['all']  -- look corresponding Enum class

    # Constants for earth's orbit eccentricity
    ## Eccentricity Offset : 0.048869
    eccentricity_phase_offset = solar_position_model_data.get(
        SolarPositionParameterMetadataColumnName.eccentricity_phase_offset, None
    )
    print(f"{eccentricity_phase_offset=}")
    ## Eccentricity Amplitude ⋅⬭ : 0.03344
    eccentricity_amplitude = solar_position_model_data.get(
        SolarPositionParameterMetadataColumnName.eccentricity_amplitude, None
    )

    # if solar_position_model.get(SHADING_STATES_COLUMN_NAME) is not None:
    #     shading_states = [state.value for state in solar_position_model.get(SHADING_STATES_COLUMN_NAME, None)]
    # else:
    #     shading_states = None

    # ----------------------------------------------------------------
    if surface_orientation or surface_tilt:
        caption += "\n[underline]Definitions[/underline]  "

    if azimuth_origin:
        caption += (
            f"Azimuth origin : [bold green]{azimuth_origin}[/bold green], "
        )

    # Fundamental Definitions

    if solar_incidence_definition is not None:
        caption += f"{SolarPositionParameterMetadataColumnName.incidence_angle.value}: [bold yellow]{solar_incidence_definition}[/bold yellow], "

    if sun_horizon_positions:
        caption += f"Sun-to-Horizon: [bold]{sun_horizon_positions}[/bold]"

    # Algorithms

    if timing_algorithm or solar_positioning_algorithm:
        caption += "\n[underline]Algorithms[/underline]  "

    if timing_algorithm:
        caption += f"Timing: [bold]{timing_algorithm}[/bold], "

    ## Timezone is part of the `time_panel`

    if solar_positioning_algorithm:
        caption += f"Positioning: [bold]{solar_positioning_algorithm}[/bold], "

    if adjusted_for_atmospheric_refraction:
        # caption += f"\n[underline]Atmospheric Properties[/underline]  "
        caption += f"Unrefracted zenith: [bold]{adjusted_for_atmospheric_refraction}[/bold], "

    if incidence_algorithm:
        caption += f"Incidence: [bold yellow]{incidence_algorithm}[/bold yellow], "

    if shading_algorithm:
        caption += f"Shading: [bold]{shading_algorithm}[/bold]"

    # if shading_states: # Not implemented for the position commands !
    #     caption += f"Shading states : [bold]{shading_states}[/bold]"

    if any([eccentricity_phase_offset, eccentricity_amplitude]):
        caption += "\n[underline]Constants[/underline] "
        if eccentricity_phase_offset and eccentricity_amplitude:
            caption += f"{SolarPositionParameterMetadataColumnName.eccentricity_phase_offset_short.value}: {eccentricity_phase_offset}, "
            caption += f"{SolarPositionParameterMetadataColumnName.eccentricity_amplitude.value}: {eccentricity_amplitude}, "

    return caption.rstrip(", ")  # Remove trailing comma + space

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
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.constants import (
    PEAK_POWER_UNIT_NAME,
    ANGLE_UNITS_COLUMN_NAME,
    AZIMUTH_ORIGIN_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME,
    INCIDENCE_ALGORITHM_COLUMN_NAME,
    INCIDENCE_DEFINITION,
    IRRADIANCE_SOURCE_COLUMN_NAME,
    LATITUDE_COLUMN_NAME,
    LONGITUDE_COLUMN_NAME,
    PEAK_POWER_COLUMN_NAME,
    ECCENTRICITY_PHASE_OFFSET_COLUMN_NAME,
    PHOTOVOLTAIC_MODULE_TYPE_NAME,
    POSITIONING_ALGORITHM_COLUMN_NAME,
    POWER_MODEL_COLUMN_NAME,
    RADIATION_MODEL_COLUMN_NAME,
    ROUNDING_PLACES_DEFAULT,
    SHADING_ALGORITHM_COLUMN_NAME,
    SHADING_STATES_COLUMN_NAME,
    SOLAR_CONSTANT_COLUMN_NAME,
    SOLAR_POSITIONS_TO_HORIZON_COLUMN_NAME,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_TILT_COLUMN_NAME,
    TECHNOLOGY_NAME,
    TIME_ALGORITHM_COLUMN_NAME,
    UNITLESS,
)
from pvgisprototype.constants import (
    REAR_SIDE_SURFACE_ORIENTATION_COLUMN_NAME,
    REAR_SIDE_SURFACE_TILT_COLUMN_NAME,
)


def build_caption_for_irradiance_data(
    longitude=None,
    latitude=None,
    elevation=None,
    timezone: ZoneInfo | None = None,
    dictionary: dict = dict(),
    rear_side_irradiance_data: dict = dict(),
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    surface_orientation=True,
    surface_tilt=True,
):
    """
    """
    caption = str()
    
    if longitude or latitude or elevation:
        caption = "[underline]Location[/underline]  "

    if longitude and latitude:
        caption += f"{LONGITUDE_COLUMN_NAME}, {LATITUDE_COLUMN_NAME} = [bold]{longitude}[/bold], [bold]{latitude}[/bold]"
    
    if elevation:
        caption += f", Elevation: [bold]{elevation} m[/bold]"

    surface_orientation = round_float_values(
        (
            dictionary.get(SURFACE_ORIENTATION_COLUMN_NAME, None)
            if surface_orientation
            else None
        ),
        rounding_places,
    )
    surface_tilt = round_float_values(
        dictionary.get(SURFACE_TILT_COLUMN_NAME, None) if surface_tilt else None,
        rounding_places,
    )

    if any(
        val is not None 
        # for val in [surface_orientation, surface_tilt, rear_side_surface_orientation, rear_side_surface_tilt]
        for val in [surface_orientation, surface_tilt]
    ):
        caption += "\n[underline]Position[/underline]  "

    if surface_orientation is not None:
        caption += (
            f"{SURFACE_ORIENTATION_COLUMN_NAME}: [bold]{surface_orientation}[/bold], "
        )

    if surface_tilt is not None:
        caption += f"{SURFACE_TILT_COLUMN_NAME}: [bold]{surface_tilt}[/bold] "

    # Rear-side ?
    if rear_side_irradiance_data:

        rear_side_surface_orientation = round_float_values(
            rear_side_irradiance_data.get(REAR_SIDE_SURFACE_ORIENTATION_COLUMN_NAME, None), 
            rounding_places
        )
        if rear_side_surface_orientation is not None:
            caption += (
                f", {REAR_SIDE_SURFACE_ORIENTATION_COLUMN_NAME}: [bold]{rear_side_surface_orientation}[/bold], "
            )
        
        rear_side_surface_tilt = round_float_values(
            rear_side_irradiance_data.get(REAR_SIDE_SURFACE_TILT_COLUMN_NAME, None), 
            rounding_places
        )
        if rear_side_surface_tilt is not None:
            caption += f"{REAR_SIDE_SURFACE_TILT_COLUMN_NAME}: [bold]{rear_side_surface_tilt}[/bold] "

    # Units for both front-side and rear-side too !  Should _be_ the same !
    units = dictionary.get(ANGLE_UNITS_COLUMN_NAME, UNITLESS)
    if (
        longitude
        or latitude
        or elevation
        or surface_orientation
        # or rear_side_surface_orientation
        or surface_tilt
        # or rear_side_surface_tilt
        and units is not None
    ):
        caption += f"  [underline]Angular units[/underline] [dim][code]{units}[/code][/dim]\n"

    irradiance_units = dictionary.get('Unit', UNITLESS)
    caption += f"[underline]Irradiance units[/underline] [dim]{irradiance_units}[/dim]"

    # Mainly about : Mono- or Bi-Facial ?
    # Maybe do the following :
    # If NOT rear_side_irradiance_data.get(PHOTOVOLTAIC_MODULE_TYPE_NAME)
    #     Then use the one from the dictionary which should be Monofacial
    # Else :
    #    Use the rear_side_irradiance_data which should be defined as Bifacial !
    photovoltaic_module_type = dictionary.get(PHOTOVOLTAIC_MODULE_TYPE_NAME, None)
    technology_name_and_type = dictionary.get(TECHNOLOGY_NAME, None)
    photovoltaic_module, mount_type = (
        technology_name_and_type.split(":")
        if technology_name_and_type
        else (None, None)
    )
    peak_power = str(dictionary.get(PEAK_POWER_COLUMN_NAME, None))
    peak_power += f' [dim]{dictionary.get(PEAK_POWER_UNIT_NAME, None)}[/dim]'

    algorithms = dictionary.get(POWER_MODEL_COLUMN_NAME, None)
    irradiance_data_source = dictionary.get(IRRADIANCE_SOURCE_COLUMN_NAME, None)
    radiation_model = dictionary.get(RADIATION_MODEL_COLUMN_NAME, None)
    equation = dictionary.get('Equation', None)

    timing_algorithm = dictionary.get(TIME_ALGORITHM_COLUMN_NAME, None)
    solar_positioning_algorithm = dictionary.get(POSITIONING_ALGORITHM_COLUMN_NAME, None)
    adjusted_for_atmospheric_refraction = dictionary.get('Unrefracted ⦧', None)
    azimuth_origin = dictionary.get(AZIMUTH_ORIGIN_COLUMN_NAME, None)
    if dictionary.get(SOLAR_POSITIONS_TO_HORIZON_COLUMN_NAME) is not None:
        solar_positions_to_horizon = [position.value for position in dictionary.get(SOLAR_POSITIONS_TO_HORIZON_COLUMN_NAME, None)]
    else:
        solar_positions_to_horizon = None
    incidence_algorithm = dictionary.get(INCIDENCE_ALGORITHM_COLUMN_NAME, None)
    shading_algorithm = dictionary.get(SHADING_ALGORITHM_COLUMN_NAME, None)

    if dictionary.get(SHADING_STATES_COLUMN_NAME) is not None:
        shading_states = [state.value for state in dictionary.get(SHADING_STATES_COLUMN_NAME, None)]
    else:
        shading_states = None

    # Review Me : What does and what does NOT make sense to have separately ?
    if rear_side_irradiance_data:
        rear_side_peak_power = str(dictionary.get(PEAK_POWER_COLUMN_NAME, None))
        rear_side_peak_power += f' [dim]{dictionary.get(PEAK_POWER_UNIT_NAME, None)}[/dim]'
        rear_side_algorithms = dictionary.get(POWER_MODEL_COLUMN_NAME, None)
    # ------------------------------------------------------------------------
    
    # Photovoltaic Module

    if photovoltaic_module:
        caption += "\n[underline]Module[/underline]  "
        caption += f"Type: [bold]{photovoltaic_module_type}[/bold], "
        caption += f"{TECHNOLOGY_NAME}: [bold]{photovoltaic_module}[/bold], "
        caption += f"Mount: [bold]{mount_type}[/bold], "
        caption += f"{PEAK_POWER_COLUMN_NAME}: [bold]{peak_power}[/bold]"

    # Fundamental Definitions

    if surface_orientation or surface_tilt:
        caption += "\n[underline]Definitions[/underline]  "

    if azimuth_origin:
        caption += f"Azimuth origin : [bold blue]{azimuth_origin}[/bold blue], "

    if timezone:
        if timezone == ZoneInfo('UTC'):
            caption += f"[bold]{timezone}[/bold], "
        else:
            caption += f"Local Zone : [bold]{timezone}[/bold], "

    solar_incidence_definition = dictionary.get(INCIDENCE_DEFINITION, None)
    if solar_incidence_definition is not None:
        caption += f"{INCIDENCE_DEFINITION}: [bold yellow]{solar_incidence_definition}[/bold yellow]"

    solar_constant = dictionary.get(SOLAR_CONSTANT_COLUMN_NAME, None)
    eccentricity_phase_offset = dictionary.get(ECCENTRICITY_PHASE_OFFSET_COLUMN_NAME, None)
    eccentricity_amplitude = dictionary.get(
        ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME, None
    )

    if solar_positions_to_horizon:
        caption += f"Positions to horizon : [bold]{solar_positions_to_horizon}[/bold], "

    # Algorithms

    if algorithms or radiation_model or timing_algorithm or solar_positioning_algorithm:
        caption += "\n[underline]Algorithms[/underline]  "

    if algorithms:
        caption += f"{POWER_MODEL_COLUMN_NAME}: [bold]{algorithms}[/bold], "

    if timing_algorithm:
        caption += f"Timing : [bold]{timing_algorithm}[/bold], "

    if solar_positioning_algorithm:
        caption += f"Positioning : [bold]{solar_positioning_algorithm}[/bold], "

    if adjusted_for_atmospheric_refraction:
        # caption += f"\n[underline]Atmospheric Properties[/underline]  "
        caption += f"Adjusted for refraction : [bold]{adjusted_for_atmospheric_refraction}[/bold], "

    if incidence_algorithm:
        caption += f"Incidence : [bold yellow]{incidence_algorithm}[/bold yellow], "

    if shading_algorithm:
        caption += f"Shading : [bold]{shading_algorithm}[/bold], "

    if radiation_model:
        caption += f"\n[underline]{RADIATION_MODEL_COLUMN_NAME}[/underline] : [bold]{radiation_model}[/bold], "
        if equation:
            #from rich.markdown import Markdown
            #markdown_equation = Markdown(f"{equation}")
            caption += f"\nEquation : [dim][code]{equation}[/code][/dim], "


    # if rear_side_shading_algorithm:
    #     caption += f"Rear-side Shading : [bold]{rear_side_shading_algorithm}[/bold]"


    # if shading_states:
    #     caption += f"Shading states : [bold]{shading_states}[/bold]"
    # if rear_side_shading_states:
    #     caption += f"Rear-side Shading states : [bold]{rear_side_shading_states}[/bold]"

    # solar_incidence_algorithm = dictionary.get(INCIDENCE_ALGORITHM_COLUMN_NAME, None)
    # if solar_incidence_algorithm is not None:
    #     caption += f"{INCIDENCE_ALGORITHM_COLUMN_NAME}: [bold yellow]{solar_incidence_algorithm}[/bold yellow], "

    if solar_constant and eccentricity_phase_offset and eccentricity_amplitude:
        caption += "\n[underline]Constants[/underline] "
        caption += f"{SOLAR_CONSTANT_COLUMN_NAME} : {solar_constant}, "
        caption += f"{ECCENTRICITY_PHASE_OFFSET_COLUMN_NAME} : {eccentricity_phase_offset}, "
        caption += f"{ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME} : {eccentricity_amplitude}, "

    # Sources ?

    if irradiance_data_source:
        caption += f"\n{IRRADIANCE_SOURCE_COLUMN_NAME}: [bold]{irradiance_data_source}[/bold], "

    return caption.rstrip(", ")  # Remove trailing comma + space

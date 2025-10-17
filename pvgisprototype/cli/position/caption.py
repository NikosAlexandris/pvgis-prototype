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
def build_solar_position_model_caption(
    main_caption,
):
    """
    """
    print(f"{model_result=}\n\n")
    print(f"{model_result.keys()=}")
    model_caption = main_caption

    # solar_positioning_algorithm = get_value_or_default(
    solar_positioning_algorithm = model_result.get(
        # model_result, POSITIONING_ALGORITHM_NAME, None
        POSITIONING_ALGORITHM_COLUMN_NAME, None
    )
    if solar_positioning_algorithm:
        model_caption += f"Positioning : [bold]{solar_positioning_algorithm}[/bold], "

    if incidence:
        # incidence_algorithm = get_value_or_default(
        incidence_algorithm = model_result.get(
            # model_result, INCIDENCE_ALGORITHM_NAME, None
            INCIDENCE_ALGORITHM_COLUMN_NAME, None
        )
        model_caption += f"Incidence : [bold yellow]{incidence_algorithm}[/bold yellow], "

    shading_algorithm = get_value_or_default(
        model_result, SHADING_ALGORITHM_NAME, None
    )
    model_caption += f"Shading : [bold]{shading_algorithm}[/bold]"

    # ----------------------------------------------------------------
    model_caption += "\n[underline]Definitions[/underline]  "

    azimuth_origin = get_value_or_default(
        model_result, AZIMUTH_ORIGIN_NAME, None
    )
    model_caption += (
        f"Azimuth origin : [bold green]{azimuth_origin}[/bold green], "
    )

    if incidence:
        incidence_angle_definition = (
            get_value_or_default(model_result, INCIDENCE_DEFINITION, None)
            if incidence
            else None
        )
        model_caption += f"Incidence angle : [bold yellow]{incidence_angle_definition}[/bold yellow]"


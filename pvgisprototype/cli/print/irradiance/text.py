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
import math
from enum import EnumType
import numpy
from rich.style import Style
from rich.text import Text
from pvgisprototype.api.position.models import ShadingState, SolarEvent, SunHorizonPositionModel
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT, SYMBOL_LOSS, SYMBOL_REFLECTIVITY


SHADING_STATE_COLOR_MAP = {
    ShadingState.sunlit: "yellow",
    ShadingState.potentially_sunlit: "dark_orange",
    ShadingState.in_shade: "gray",
}


SOLAR_EVENT_COLOR_MAP = {
    SolarEvent.astronomical_twilight: "bold dark_blue",
    SolarEvent.nautical_twilight: "bold orange4",
    SolarEvent.civil_twilight: "bold dark_goldenrod",
    SolarEvent.sunrise: "bold orange1",
    SolarEvent.noon: "bold yellow",
    SolarEvent.sunset: "bold blue_violet",
}


SUN_HORIZON_POSITION_COLOR_MAP = {
    SunHorizonPositionModel.above.value: "bold yellow",
    SunHorizonPositionModel.low_angle.value: "dark_orange",
    SunHorizonPositionModel.below.value: "red",
}


def format_string(
    value: str | int | float | Style,
    # enum_model: EnumType,
    column_name=None,
    rounding_places=ROUNDING_PLACES_DEFAULT,
):
    """
    """
    # Handle None
    if value is None:
        return ""

    if isinstance(value, (EnumType, str)):

        if value in [string.value for string in ShadingState]:
            style = SHADING_STATE_COLOR_MAP.get(value, None)
            return Text(value, style=style)

        # Handle SolarEvent
        if value in [string.value for string in SolarEvent]:
            style = SOLAR_EVENT_COLOR_MAP.get(value, None)
            return Text(value, style=style)

        # Handle SunHorizonPositionModel
        if value in [string.value for string in SunHorizonPositionModel]:
            style = str(SUN_HORIZON_POSITION_COLOR_MAP.get(str(value)))
            return Text(value, style=style)

    # Handle negative numbers or loss columns
    else:
        rounded_value = round_float_values(value, rounding_places)

        # If values of this column are negative / represent loss
        if (
            f" {SYMBOL_LOSS}" in column_name
            or f"{SYMBOL_REFLECTIVITY}" in column_name
            or value < 0
        ):  # Avoid matching any `-`

            # Make them bold red
            return Text(str(rounded_value), style="bold red")

        elif isinstance(value, (numpy.number, float)) and value ==0.:
            return Text(str(rounded_value), style="dim gray")

        elif (isinstance(value, float) and (math.isnan(value))) or (
            isinstance(value, numpy.floating) and numpy.isnan(value)
        ):
            return Text(str(value), style="dim red")


        else:
            return str(rounded_value)

    # Fallback: just return as string
    return str(value)

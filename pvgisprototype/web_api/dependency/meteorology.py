from typing import Annotated
import numpy as np
from pvgisprototype import (
    LinkeTurbidityFactor,
    TemperatureSeries,
    WindSpeedSeries,
)
from pvgisprototype.constants import (
    SYMBOL_UNIT_TEMPERATURE,
    SYMBOL_UNIT_WIND_SPEED,
    TEMPERATURE_DEFAULT,
    WIND_SPEED_DEFAULT,
)
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_linke_turbidity_factor_series,
)


async def create_temperature_series(
    temperature_series: float | None = None,
) -> TemperatureSeries:
    """ """
    if isinstance(temperature_series, float):
        return TemperatureSeries(
            value=np.array(temperature_series, dtype=np.float32),
            unit=SYMBOL_UNIT_TEMPERATURE,
        )

    return TemperatureSeries(
        value=np.array(TEMPERATURE_DEFAULT, dtype=np.float32),
        unit=SYMBOL_UNIT_TEMPERATURE,
    )


async def create_wind_speed_series(
    wind_speed_series: float | None = None,
) -> WindSpeedSeries:
    """ """
    if isinstance(wind_speed_series, float):
        return WindSpeedSeries(
            value=np.array(wind_speed_series), unit=SYMBOL_UNIT_WIND_SPEED
        )

    return WindSpeedSeries(
        value=np.array(WIND_SPEED_DEFAULT), unit=SYMBOL_UNIT_WIND_SPEED
    )


async def process_linke_turbidity_factor_series(
    linke_turbidity_factor_series: Annotated[
        float, fastapi_query_linke_turbidity_factor_series
    ] = LinkeTurbidityFactor(),
) -> LinkeTurbidityFactor:
    """ """
    return LinkeTurbidityFactor(value=linke_turbidity_factor_series)

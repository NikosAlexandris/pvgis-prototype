from typing import Annotated
from fastapi import Depends, HTTPException

from pvgisprototype.algorithms.tmy.models import TMYStatisticModel
from pvgisprototype.algorithms.tmy.weighting_scheme_model import MeteorologicalVariable
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.constants import (
    IN_MEMORY_FLAG_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_end_time,
    fastapi_query_in_memory,
    fastapi_query_latitude_in_degrees,
    fastapi_query_longitude_in_degrees,
    fastapi_query_mask_and_scale,
    fastapi_query_meteorological_variable,
    fastapi_query_neighbor_lookup,
    fastapi_query_periods,
    fastapi_query_start_time,
    fastapi_query_tmy_statistic_model,
    fastapi_query_tolerance,
)
from pvgisprototype.web_api.schemas import Frequency
from pvgisprototype.web_api.dependency.common_datasets import (
    _provide_common_datasets,
    process_timestamps,
)
from pvgisprototype.web_api.dependency.time import (
    process_frequency,
)
from pvgisprototype.web_api.dependency.verbosity import process_verbose


async def tmy_statistic_model(
    plot_statistic: Annotated[
        TMYStatisticModel | None, fastapi_query_tmy_statistic_model  # type: ignore
    ] = None,
) -> TMYStatisticModel:  # type: ignore

    NOT_IMPLEMENTED_YET = [
        TMYStatisticModel.ranked,
        TMYStatisticModel.weighted,
        TMYStatisticModel.finkelsteinschafer,
        TMYStatisticModel.yearly_ecdf,
        TMYStatisticModel.long_term_ecdf,
        TMYStatisticModel.all,
    ]

    if plot_statistic in NOT_IMPLEMENTED_YET:
        raise HTTPException(
            status_code=400,
            detail=f"Option {plot_statistic} is not currently supported!",
        )

    return plot_statistic


async def _select_data_from_meteorological_variable(
    common_datasets: Annotated[dict, Depends(_provide_common_datasets)],
    meteorological_variable: Annotated[
        MeteorologicalVariable, fastapi_query_meteorological_variable
    ] = MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE,
    longitude: Annotated[float, fastapi_query_longitude_in_degrees] = 8.628,
    latitude: Annotated[float, fastapi_query_latitude_in_degrees] = 45.812,
    timestamps: Annotated[str | None, Depends(process_timestamps)] = None,
    start_time: Annotated[
        str | None, fastapi_query_start_time
    ] = "2010-01-01",  # Used by fastapi_query_start_time
    periods: Annotated[
        int | None, fastapi_query_periods
    ] = None,  # Used by fastapi_query_periods
    frequency: Annotated[Frequency, Depends(process_frequency)] = Frequency.Hourly,
    end_time: Annotated[
        str | None, fastapi_query_end_time
    ] = "2020-12-31",  # Used by fastapi_query_end_time
    neighbor_lookup: Annotated[
        MethodForInexactMatches, fastapi_query_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float, fastapi_query_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, fastapi_query_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, fastapi_query_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    verbose: Annotated[int, Depends(process_verbose)] = VERBOSE_LEVEL_DEFAULT,
):
    meteorological_variable_file_mapping = {
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: common_datasets[
            "temperature_series"
        ],
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: common_datasets[
            "global_horizontal_irradiance_series"
        ],
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: None,
        MeteorologicalVariable.MEAN_WIND_SPEED: common_datasets["wind_speed_series"],
        MeteorologicalVariable.MEAN_DEW_POINT_TEMPERATURE: None,
        MeteorologicalVariable.MEAN_RELATIVE_HUMIDITY: None,
        MeteorologicalVariable.MAX_DEW_POINT_TEMPERATURE: None,
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: None,
        MeteorologicalVariable.MAX_WIND_SPEED: None,
        MeteorologicalVariable.MIN_DEW_POINT_TEMPERATURE: None,
        MeteorologicalVariable.all: None,
    }

    file_variable_mapping = {
        common_datasets["temperature_series"]: "era5_t2m",
        common_datasets["wind_speed_series"]: "era5_ws2m",
        common_datasets["global_horizontal_irradiance_series"]: "sarah3_sis",
        common_datasets["direct_horizontal_irradiance_series"]: "sarah3_sid",
    }  # NOTE Add more here...

    if meteorological_variable_file_mapping[meteorological_variable]:
        variable = file_variable_mapping[
            meteorological_variable_file_mapping[meteorological_variable]
        ]
        data_array = select_time_series(
            time_series=meteorological_variable_file_mapping[meteorological_variable],
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            mask_and_scale=mask_and_scale,  # True ?
            neighbor_lookup=neighbor_lookup,
            tolerance=tolerance,
            in_memory=in_memory,
            verbose=verbose,
        )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Option {meteorological_variable} is not currently supported!",
        )  # NOTE This MUST be removed when all data will be supported!

    return {
        "variable": variable,
        "data_array": data_array,
    }

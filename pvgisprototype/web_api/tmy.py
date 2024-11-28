from fastapi import HTTPException, Request
from pandas import DatetimeIndex
from typing_extensions import Annotated

from pvgisprototype.algorithms.tmy.models import (
    FinkelsteinSchaferStatisticModel,
    TMYStatisticModel,
    select_meteorological_variables,
    select_tmy_models,
)
from pvgisprototype.algorithms.tmy.weighting_scheme_model import (
    TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT,
    MeteorologicalVariable,
    TypicalMeteorologicalMonthWeightingScheme,
)
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.api.quick_response_code import QuickResponseCode
from pvgisprototype.api.tmy.tmy import calculate_tmy
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.constants import (
    FINGERPRINT_FLAG_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    METADATA_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    NOT_AVAILABLE,
    QUIET_FLAG_DEFAULT,
    STATISTICS_FLAG_DEFAULT,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.web_api.dependencies import (
    fastapi_dependable_angle_output_units,
    fastapi_dependable_common_datasets,
    fastapi_dependable_fingerprint,
    fastapi_dependable_frequency,
    fastapi_dependable_groupby,
    fastapi_dependable_latitude,
    fastapi_dependable_longitude,
    fastapi_dependable_quiet,
    fastapi_dependable_read_datasets,
    fastapi_dependable_select_data_from_meteorological_variable,
    fastapi_dependable_timestamps,
    fastapi_dependable_tmy_statistic_model,
    fastapi_dependable_verbose,
    fastapi_query_quick_response_code,
)
from pvgisprototype.web_api.fastapi_parameters import (
    fastapi_query_csv,
    fastapi_query_end_time,
    fastapi_query_in_memory,
    fastapi_query_latitude_in_degrees,
    fastapi_query_longitude_in_degrees,
    fastapi_query_mask_and_scale,
    fastapi_query_meteorological_variable,
    fastapi_query_neighbor_lookup,
    fastapi_query_periods,
    fastapi_query_start_time,
    fastapi_query_statistics,
    fastapi_query_tolerance,
    fastapi_query_variable,
    fastapi_query_weighting_scheme,
)
from pvgisprototype.web_api.schemas import AngleOutputUnit, Frequency, GroupBy


def get_metadata(request: Request):
    return {"Input query parameters": dict(request.query_params)}


async def get_tmy(
    request: Request,
    _select_data_from_meteorological_variable: Annotated[
        dict, fastapi_dependable_select_data_from_meteorological_variable
    ],
    meteorological_variable: Annotated[
        MeteorologicalVariable, fastapi_query_meteorological_variable
    ] = MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE,
    longitude: Annotated[float, fastapi_query_longitude_in_degrees] = 8.628,
    latitude: Annotated[float, fastapi_query_latitude_in_degrees] = 45.812,
    start_time: Annotated[
        str | None, fastapi_query_start_time
    ] = "2015-01-01",  # Used by fastapi_query_start_time
    periods: Annotated[
        int | None, fastapi_query_periods
    ] = None,  # Used by fastapi_query_periods
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hourly,
    end_time: Annotated[
        str | None, fastapi_query_end_time
    ] = "2020-12-31",  # Used by fastapi_query_end_time
    timestamps: Annotated[DatetimeIndex | None, fastapi_dependable_timestamps] = None,
    variable: Annotated[str | None, fastapi_query_variable] = None,
    neighbor_lookup: Annotated[
        MethodForInexactMatches, fastapi_query_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float, fastapi_query_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, fastapi_query_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, fastapi_query_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    statistics: Annotated[bool, fastapi_query_statistics] = STATISTICS_FLAG_DEFAULT,
    # csv: Annotated[str | None, fastapi_query_csv] = None,
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_dependable_angle_output_units
    ] = AngleOutputUnit.RADIANS,
    weighting_scheme: Annotated[
        TypicalMeteorologicalMonthWeightingScheme, fastapi_query_weighting_scheme
    ] = TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT,
    plot_statistic: Annotated[
        TMYStatisticModel, fastapi_dependable_tmy_statistic_model
    ] = TMYStatisticModel.tmy,
    verbose: Annotated[int, fastapi_dependable_verbose] = VERBOSE_LEVEL_DEFAULT,
    quiet: Annotated[bool, fastapi_dependable_quiet] = QUIET_FLAG_DEFAULT,
    fingerprint: Annotated[
        bool, fastapi_dependable_fingerprint
    ] = FINGERPRINT_FLAG_DEFAULT,
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
    metadata: bool = METADATA_FLAG_DEFAULT,
):

    meteorological_variables = select_meteorological_variables(
        MeteorologicalVariable, [meteorological_variable]
    )  # Using a callback fails!

    tmy = calculate_tmy(
        time_series=_select_data_from_meteorological_variable["data_array"],
        meteorological_variables=meteorological_variables,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        start_time=start_time,
        periods=periods,
        frequency=frequency,
        end_time=end_time,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        in_memory=in_memory,
        weighting_scheme=weighting_scheme,
        verbose=verbose,
    )

    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)

    response: dict = {}  # type: ignore

    headers = {"Content-Disposition": f'attachment; filename=TMY.json"'}

    response["headers"] = headers

    if quick_response_code.value != QuickResponseCode.NoneValue:
        raise HTTPException(
            status_code=400,
            detail=f"Option quick_response_code: {quick_response_code} is not currently supported!",
        )

    if not quiet:
        if verbose > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Option verbose: {verbose} is not currently supported!",
            )
        else:
            flat_list = []
            for meteorological_variable in meteorological_variables:
                statistic_values = tmy.get(meteorological_variable)
                for data_array in statistic_values.get(
                    FinkelsteinSchaferStatisticModel.ranked, NOT_AVAILABLE
                ):
                    flat_list.extend(data_array.values.flatten().astype(str))
                csv_str = ",".join(flat_list)

                response["TMY"] = csv_str

    if plot_statistic:
        from io import BytesIO

        from fastapi.responses import StreamingResponse

        from pvgisprototype.algorithms.tmy.models import PLOT_FUNCTIONS

        meteorological_variable_statistics = tmy.get(meteorological_variable)

        if plot_statistic == TMYStatisticModel.tmy:
            plot_function = PLOT_FUNCTIONS.get(plot_statistic)
            if plot_function is not None:
                figure = plot_function(
                    tmy_series=meteorological_variable_statistics.get(
                        plot_statistic.value
                    ),
                    variable=_select_data_from_meteorological_variable["variable"],
                    finkelstein_schafer_statistic=meteorological_variable_statistics.get(
                        "Finkelstein-Schafer"
                    ),
                    typical_months=meteorological_variable_statistics.get(
                        "Typical months"
                    ),
                    input_series=meteorological_variable_statistics.get(
                        meteorological_variable
                    ),
                    title="Typical Meteorological Year",
                    y_label=meteorological_variable.value,
                    weighting_scheme=weighting_scheme,
                    fingerprint=fingerprint,
                    to_file=False,
                )
            else:
                raise ValueError(
                    f"Plot function for statistic {plot_function} not found."
                )

        elif plot_statistic == TMYStatisticModel.ranked:
            plot_function = PLOT_FUNCTIONS.get(plot_statistic.value)
            if plot_function is not None:
                plot_function(
                    ranked_finkelstein_schafer_statistic=tmy.get(plot_statistic.value),
                    weighting_scheme=weighting_scheme,
                )
            else:
                raise ValueError(
                    f"Plot function for statistic {plot_function} not found."
                )
        else:
            plot_function = PLOT_FUNCTIONS.get(plot_statistic)
            if plot_function is not None:
                plot_function(tmy.get(plot_statistic.value, None))
            else:
                raise ValueError(
                    f"Plot function for statistic {plot_function} not found."
                )

        # Serialize the figure to a PNG image in memory
        buffer = BytesIO()
        figure.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)  # Reset the buffer pointer to the beginning

        return StreamingResponse(buffer, media_type="image/png")

    if fingerprint:
        raise HTTPException(
            status_code=400,
            detail=f"Option fingerprint: {fingerprint} is not currently supported!",
        )

    if metadata:
        response["Metadata"] = get_metadata(request=request)  # type: ignore

    return response

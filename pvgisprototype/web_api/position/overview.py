from typing import Annotated, List
from urllib.parse import quote

from fastapi import Query, Depends
from fastapi.responses import ORJSONResponse, PlainTextResponse, StreamingResponse
from pandas import DatetimeIndex

from pvgisprototype.api.position.models import (
    ShadingModel,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.api.position.overview import (
    calculate_solar_position_overview_series,
)
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.constants import (
    ECCENTRICITY_CORRECTION_FACTOR,
    PERIGEE_OFFSET,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
)
from pvgisprototype.web_api.dependencies import (
    fastapi_dependable_angle_output_units,
    fastapi_dependable_convert_timestamps,
    fastapi_dependable_convert_timezone,
    fastapi_dependable_frequency,
    fastapi_dependable_latitude,
    fastapi_dependable_longitude,
    fastapi_dependable_solar_incidence_models,
    fastapi_dependable_solar_position_models_list,
    fastapi_dependable_surface_orientation,
    fastapi_dependable_surface_tilt,
    fastapi_dependable_timestamps,
    fastapi_dependable_timezone,
    process_timestamps_override_timestamps_from_data,
    convert_timestamps_to_specified_timezone_override_timestamps_from_data,
)
from pvgisprototype.web_api.fastapi_parameters import (
    fastapi_query_apply_atmospheric_refraction,
    fastapi_query_csv,
    fastapi_query_elevation,
    fastapi_query_end_time,
    fastapi_query_perigee_offset,
    fastapi_query_periods,
    fastapi_query_start_time,
    fastapi_query_zero_negative_solar_incidence_angle,
)
from pvgisprototype.web_api.schemas import (
    AngleOutputUnit,
    Frequency,
    Timezone,
)
from pvgisprototype.constants import FINGERPRINT_FLAG_DEFAULT
from pvgisprototype.web_api.fastapi_parameters import (
    fastapi_query_verbose,
    fastapi_query_fingerprint,
)
from pvgisprototype.web_api.dependencies import fastapi_dependable_horizon_profile
from pvgisprototype.web_api.dependencies import fastapi_dependable_shading_model
from pvgisprototype.api.position.models import SolarPositionParameter


async def get_calculate_solar_position_overview(
    longitude: Annotated[float, fastapi_dependable_longitude] = 8.628,
    latitude: Annotated[float, fastapi_dependable_latitude] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214.0,
    surface_orientation: Annotated[
        float, fastapi_dependable_surface_orientation
    ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[
        float, fastapi_dependable_surface_tilt
    ] = SURFACE_TILT_DEFAULT,
    timestamps: Annotated[
        str | None, Depends(process_timestamps_override_timestamps_from_data)
    ] = None,
    start_time: Annotated[str | None, fastapi_query_start_time] = "2014-01-01 00:00:00",
    periods: Annotated[str | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hourly,
    end_time: Annotated[str | None, fastapi_query_end_time] = "2014-12-31 23:59:59",
    timezone: Annotated[Timezone, fastapi_dependable_timezone] = Timezone.UTC,  # type: ignore[attr-defined]
    solar_position_models: Annotated[
        List[SolarPositionModel], fastapi_dependable_solar_position_models_list
    ] = [SolarPositionModel.noaa],
    solar_incidence_model: Annotated[
        SolarIncidenceModel, fastapi_dependable_solar_incidence_models
    ] = SolarIncidenceModel.iqbal,
    horizon_profile: Annotated[str | None, fastapi_dependable_horizon_profile] = None,
    shading_model: Annotated[
        ShadingModel, fastapi_dependable_shading_model
    ] = ShadingModel.pvis,
    zero_negative_solar_incidence_angle: Annotated[
        bool, fastapi_query_zero_negative_solar_incidence_angle
    ] = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    apply_atmospheric_refraction: Annotated[
        bool, fastapi_query_apply_atmospheric_refraction
    ] = True,
    solar_time_model: SolarTimeModel = Query(SolarTimeModel.milne),
    perigee_offset: Annotated[float, fastapi_query_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = Query(ECCENTRICITY_CORRECTION_FACTOR),
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_dependable_angle_output_units
    ] = AngleOutputUnit.RADIANS,
    csv: Annotated[str | None, fastapi_query_csv] = None,
    fingerprint: Annotated[bool, fastapi_query_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
    timezone_for_calculations: Annotated[  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
        Timezone, fastapi_dependable_convert_timezone
    ] = Timezone.UTC,  # type: ignore[attr-defined]
    user_requested_timestamps: Annotated[
        DatetimeIndex | None,
        Depends(convert_timestamps_to_specified_timezone_override_timestamps_from_data),
    ] = None,  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
):
    """
    Calculate the solar position parameters for a solar surface based on its orientation, tilt, and geographic location over a given time series.
    The calculation incorporates user-specified solar position models (e.g., positioning algorithms) and a selected solar time model (e.g., solar timing algorithm).

    ## **Important Notes**

    - While it is straightforward to report the solar position parameters for a
     series of solar position models (positioning algorithms), offering the
     option for multiple solar time models (timing algorithms), would mean to
     carefully craft the combinations for each solar time model and solar
     position models. Not impossible, yet something for expert users that would
     like to assess different combinations of algorithms to explore and assess
     solar position parameters.

    - The default time, if not given, regardless of the `frequency` is
      `00:00:00`. It is then expected to get `0` incoming solar irradiance and
      subsequently photovoltaic power/energy output.

    - Of the four parameters `start_time`, `end_time`, `periods`, and
      `frequency`, exactly three must be specified. If `frequency` is omitted,
      the resulting timestamps (a Pandas `DatetimeIndex` object)
      will have `periods` linearly spaced elements between `start_time` and
      `end_time` (closed on both sides). Learn more about frequency strings at
      [Offset aliases](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases).

    """
    solar_position_series = calculate_solar_position_overview_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone_for_calculations,  # type: ignore[arg-type]
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        solar_position_models=solar_position_models,
        solar_incidence_model=solar_incidence_model,
        horizon_profile=horizon_profile,  # type: ignore[arg-type]
        shading_model=shading_model,
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        solar_time_model=solar_time_model,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
        fingerprint=fingerprint,
        verbose=verbose,
    )

    # -------------------------------------------------------------- Important
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    # ------------------------------------------------------------------------

    if csv:
        import io
        import zipfile

        from pvgisprototype.web_api.utilities import generate_photovoltaic_output_csv

        if len(solar_position_models) > 1:
            # Create an in-memory ZIP file buffer
            zip_buffer = io.BytesIO()
            # Use zipfile to create the archive with maximum efficiency
            with zipfile.ZipFile(
                zip_buffer, "w", compression=zipfile.ZIP_DEFLATED
            ) as zip_file:
                # Generate and write each CSV file to the ZIP archive
                for solar_position_model in solar_position_models:
                    # Generate the CSV content for the current model
                    in_memory_csv = generate_photovoltaic_output_csv(
                        dictionary=solar_position_series[solar_position_model.name],
                        latitude=latitude,
                        longitude=longitude,
                        timestamps=user_requested_timestamps,
                        timezone=timezone,  # type: ignore
                    )

                    # Write CSV content directly to the ZIP archive
                    zip_file.writestr(
                        f"{solar_position_model.name}.csv", in_memory_csv  # type: ignore[arg-type]
                    )

            # Reset the buffer's position to the beginning for reading
            zip_buffer.seek(0)

            # Return the ZIP file as a streaming response
            response = StreamingResponse(
                zip_buffer,
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename={quote(csv)}.zip"
                },
            )
        else:
            in_memory_csv = generate_photovoltaic_output_csv(
                dictionary=solar_position_series[solar_position_models[0].name],
                latitude=latitude,
                longitude=longitude,
                timestamps=user_requested_timestamps,
                timezone=timezone,  # type: ignore
            )
            response = PlainTextResponse(  # type: ignore[assignment]
                in_memory_csv,
                media_type="application/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={quote(csv)}.csv"
                },
            )

        return response  # type: ignore

    response: dict = {}  # type: ignore
    headers = {"Content-Disposition": f'attachment; filename="solar_position.json"'}

    # NOTE Loop through models and in the case of sun horizon parameters in order for orjon to be able to serialize the numpy.array[str,] we need to convert it to list first
    # NOTE This is a workaround for this issue #314. Library orjson does not support serializing of numpy arrays of datatype string
    for solar_position_model in solar_position_models:
        if (
            solar_position_series[solar_position_model.name][
                SolarPositionParameter.sun_horizon
            ]
            is not None
        ) and (
            not isinstance(
                solar_position_series[solar_position_model.name][
                    SolarPositionParameter.sun_horizon
                ],
                str,
            )
        ):
            solar_position_series[solar_position_model.name][
                SolarPositionParameter.sun_horizon
            ] = solar_position_series[solar_position_model.name][
                SolarPositionParameter.sun_horizon
            ].tolist()

    response["Results"] = solar_position_series  # type: ignore[index]

    return ORJSONResponse(response, headers=headers, media_type="application/json")

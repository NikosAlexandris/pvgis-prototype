from datetime import date
from pathlib import Path
from typing import Annotated, Any

import numpy as np
import orjson
from fastapi import Request
from fastapi.responses import Response
from fastapi.responses import JSONResponse
from fastapi.responses import ORJSONResponse
from pandas import DatetimeIndex, to_datetime


from pvgisprototype import LinkeTurbidityFactor, SpectralFactorSeries
from pvgisprototype.api.irradiance.models import (
    MethodForInexactMatches,
    ModuleTemperatureAlgorithm,
)
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.api.power.broadband import (
    calculate_photovoltaic_power_output_series,
)
from pvgisprototype.api.power.broadband_multiple_surfaces import (
    calculate_photovoltaic_power_output_series_from_multiple_surfaces,
)
from pvgisprototype.api.power.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.power.performance import summarise_photovoltaic_performance
from pvgisprototype.api.quick_response_code import generate_quick_response_code
from pvgisprototype.api.quick_response_code import QuickResponseCode
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.constants import (
    CSV_FLAG_DEFAULT,
    DEGREES,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    METADATA_FLAG_DEFAULT,
    NOT_AVAILABLE,
    PEAK_POWER_DEFAULT,
    PHOTOVOLTAIC_PERFORMANCE_ANALYSIS_OUTPUT_FILENAME,
    PHOTOVOLTAIC_PERFORMANCE_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_OUTPUT_FILENAME,
    QUICK_RESPONSE_CODE_FLAG_DEFAULT,
    RADIATION_CUTOFF_THRESHHOLD,
    ALBEDO_DEFAULT,
    ANALYSIS_FLAG_DEFAULT,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    PERIGEE_OFFSET,
    QUIET_FLAG_DEFAULT,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    SOLAR_CONSTANT,
    STATISTICS_FLAG_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SYSTEM_EFFICIENCY_DEFAULT,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
)
from pvgisprototype.web_api.dependencies import (
    fastapi_dependable_angle_output_units,
    fastapi_dependable_frequency,
    fastapi_dependable_groupby,
    fastapi_dependable_latitude,
    fastapi_dependable_linke_turbidity_factor_series,
    fastapi_dependable_longitude,
    fastapi_dependable_refracted_solar_zenith,
    fastapi_dependable_solar_position_models,
    fastapi_dependable_spectral_factor_series,
    fastapi_dependable_surface_orientation,
    fastapi_dependable_surface_orientation_list,
    fastapi_dependable_surface_tilt,
    fastapi_dependable_surface_tilt_list,
    fastapi_dependable_timestamps,
    fastapi_dependable_timezone,
    # fastapi_dependable_csv,
    fastapi_dependable_verbose,
    fastapi_dependable_fingerprint,
)
from pvgisprototype.web_api.fastapi_parameters import (
    fastapi_query_efficiency,
    fastapi_query_temperature_model,
    fastapi_query_radiation_cutoff_threshold,
    fastapi_query_albedo,
    fastapi_query_analysis,
    fastapi_query_csv,
    fastapi_query_elevation,
    fastapi_query_end_time,
    fastapi_query_fingerprint,
    fastapi_query_peak_power,
    fastapi_query_periods,
    fastapi_query_photovoltaic_module_model,
    fastapi_query_power_model,
    fastapi_query_quick_response_code,
    fastapi_query_index,
    fastapi_query_quiet,
    fastapi_query_solar_time_model,
    fastapi_query_start_time,
    fastapi_query_statistics,
    fastapi_query_system_efficiency,
    fastapi_query_tolerance,
    fastapi_query_zero_negative_solar_incidence_angle,
)
from pvgisprototype.web_api.schemas import AnalysisLevel, AngleOutputUnit, Frequency, GroupBy, Timezone, VerbosityLevel


def get_metadata(request: Request):
    return {"Input query parameters": dict(request.query_params)}
    # return JSONResponse()


def convert_numpy_arrays_to_lists(data: Any) -> Any:
    """Convert all NumPy arrays and other NumPy types in the input to native Python types.

    Parameters
    ----------
    data : Any
        The input data possibly containing NumPy arrays and other NumPy types.

    Returns
    -------
    Any
        A new data structure with all NumPy arrays converted to lists and other NumPy types converted to native types.
    """
    if isinstance(data, dict):
        return {k: convert_numpy_arrays_to_lists(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_arrays_to_lists(v) for v in data]
    elif isinstance(data, tuple):
        return tuple(convert_numpy_arrays_to_lists(v) for v in data)
    elif isinstance(data, np.datetime64):
        return to_datetime(str(data)).isoformat()
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, (np.float64, np.float32)):
        return float(data)
    else:
        return data


async def get_photovoltaic_performance_analysis(
    request: Request,
    longitude: Annotated[float, fastapi_dependable_longitude] = 8.628,
    latitude: Annotated[float, fastapi_dependable_latitude] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214.0,
    surface_orientation: Annotated[float, fastapi_dependable_surface_orientation ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[float, fastapi_dependable_surface_tilt ] = SURFACE_TILT_DEFAULT,
    start_time: Annotated[str | None, fastapi_query_start_time] = '2013-01-01',  # Used by fastapi_query_start_time
    periods: Annotated[str | None, fastapi_query_periods] = None,  # Used by fastapi_query_periods
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hourly,
    end_time: Annotated[str | None, fastapi_query_end_time] = '2013-12-31', # Used by fastapi_query_end_time
    timestamps: Annotated[DatetimeIndex|None, fastapi_dependable_timestamps] = None,
    timezone: Annotated[Timezone, fastapi_dependable_timezone] = Timezone.UTC,  # type: ignore[attr-defined]
    photovoltaic_module: Annotated[ PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model ] = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    system_efficiency: Annotated[float, fastapi_query_system_efficiency ] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[PhotovoltaicModulePerformanceModel, fastapi_query_power_model] = PhotovoltaicModulePerformanceModel.king,
    peak_power: Annotated[float, fastapi_query_peak_power] = PEAK_POWER_DEFAULT,
    # statistics: Annotated[bool, fastapi_query_statistics] = STATISTICS_FLAG_DEFAULT,
    # groupby: Annotated[GroupBy, fastapi_dependable_groupby] = GroupBy.N,
    analysis: Annotated[AnalysisLevel, fastapi_query_analysis] = AnalysisLevel.Simple,
    csv: Annotated[str | None, fastapi_query_csv] = None,
    verbose: Annotated[int, fastapi_dependable_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, fastapi_query_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, fastapi_query_quiet] = True,  # Keep me hardcoded !
    fingerprint: Annotated[bool, fastapi_dependable_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    # metadata: Annotated[bool, typer_option_command_metadata] = METADATA_FLAG_DEFAULT,
    metadata: bool = METADATA_FLAG_DEFAULT,
    quick_response_code: Annotated[QuickResponseCode, fastapi_query_quick_response_code] = QuickResponseCode.NoneValue,
) -> Response:
    """Analyse the photovoltaic performance for a solar surface, various
    technologies, free-standing or building-integrated, at a specific location
    and a given period.

    ### Input time series

    This function consumes internally :
    
    - time series data limited to the period **2005** - **2023**.
    - solar irradiance from the [SARAH3 climate records](https://wui.cmsaf.eu/safira/action/viewDoiDetails?acronym=SARAH_V003) (produced by the German Weather Service)
    - temperature and wind speed estimations from [ERA5 Reanalysis](https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5) collection
    - spectral effect factor time series (Huld, 2011) _for the reference year 2013_

    ### Features

    - Arbitrary time series supported by [Pandas' DatetimeIndex](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html) 
    - Surface position optimisation supported by [SciPy](https://docs.scipy.org/doc/scipy/reference/optimize.html) (**pending integration**)
    - Get from simple to detailed output in form of **JSON**, **CSV** and **Excel** (the latter **pending implementation**)
    - Share a **QR-Code** with a summary of the analysis
    - **Fingerprint** your analysis
    - Document your analysis including all **input metadata**

    ### Need more control ?

    In the `/performance/advanced` endpoint you may find :

    - Optional algorithms for solar timing, positioning and the estimation of the solar incidence angle
    - Disable atmospheric refraction for solar positioning
    - Simpler power-rating model as well as module temperature model
    - and more

    """
    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        timestamps=timestamps,
        timezone=timezone,
        global_horizontal_irradiance=Path(
            "sarah2_sis_over_esti_jrc.nc"
        ),  # FIXME This hardwritten path will be replaced
        direct_horizontal_irradiance=Path(
            "sarah2_sid_over_esti_jrc.nc"
        ),  # FIXME This hardwritten path will be replaced
        spectral_factor_series=Path(
            "spectral_effect_cSi_2013_over_esti_jrc.nc"
            ),
        temperature_series=Path(
            "era5_t2m_over_esti_jrc.nc"
        ),  # FIXME This hardwritten path will be replaced
        wind_speed_series=Path(
            "era5_ws2m_over_esti_jrc.nc"
        ),  # FIXME This hardwritten path will be replaced
        photovoltaic_module=photovoltaic_module,
        system_efficiency=system_efficiency,
        power_model=power_model,
        peak_power=peak_power,
        angle_output_units=DEGREES,
        verbose=verbose,
        fingerprint=fingerprint,
    )

    # -------------------------------------------------------------- Important
    angle_output_units = DEGREES
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    # ------------------------------------------------------------------------

    if csv:
        from datetime import datetime

        from fastapi.responses import StreamingResponse

        # streaming_data = [(str(timestamp), photovoltaic_power) for timestamp, photovoltaic_power in zip(timestamps.tolist(), photovoltaic_power_output_series.value.tolist())]  # type: ignore
        filename = 'filename.csv'
        # filename = f"photovoltaic_power_output_{photovoltaic_power_output_series.components[FINGERPRINT_COLUMN_NAME]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        # csv_content = ",".join(["Timestamp", "Photovoltaic Power"]) + "\n"
        # csv_content += (
        #     "\n".join(
        #         [
        #             ",".join([timestamp, str(photovoltaic_power)])
        #             for timestamp, photovoltaic_power in streaming_data
        #         ]
        #     )
        #     + "\n"
        # )

        dictionary = photovoltaic_power_output_series.components
        # remove 'Title' and 'Fingerprint' : we don't want repeated values ! ----
        dictionary.pop('Title', NOT_AVAILABLE)
        fingerprint = dictionary.pop(FINGERPRINT_COLUMN_NAME, NOT_AVAILABLE)
        # ------------------------------------------------------------- Important

        header = []
        if index:
            header.insert(0, 'Index')
        if longitude:
            header.append('Longitude')
        if latitude:
            header.append('Latitude')

        header.append('Time')
        header.extend(dictionary.keys())

        # Convert single float or int values to arrays of the same length as timestamps
        for key, value in dictionary.items():
            if isinstance(value, (float, int)):
                dictionary[key] = np.full(len(timestamps), value)
            if isinstance(value, str):
                dictionary[key] = np.full(len(timestamps), str(value))
        
        # Zip series and timestamps
        zipped_series = zip(*dictionary.values())
        zipped_data = zip(timestamps, zipped_series)
        
        rows = []
        for idx, (timestamp, values) in enumerate(zipped_data):
            row = []
            if index:
                row.append(idx)
            if longitude and latitude:
                row.extend([longitude, latitude])
            row.append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))
            row.extend(values)
            rows.append(row)

        csv_content = ",".join(header) + "\n"
        csv_content += "\n".join([",".join(map(str, row)) for row in rows])

        response_csv = StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
        return response_csv

    response = {}
    if fingerprint:
        response[FINGERPRINT_COLUMN_NAME] = photovoltaic_power_output_series.components[
            FINGERPRINT_COLUMN_NAME
        ]

    if not quiet:
        if verbose > 0:
            response = convert_numpy_arrays_to_lists(
                photovoltaic_power_output_series.components
            )
        else:
            response = {
                PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_output_series.value,
            }
            headers = {
                "Content-Disposition": f'attachment; filename="{PHOTOVOLTAIC_POWER_OUTPUT_FILENAME}.json"'
            }

    # if statistics:
    #     from pvgisprototype.api.series.statistics import calculate_series_statistics

    #     series_statistics = calculate_series_statistics(
    #         data_array=photovoltaic_power_output_series.value,
    #         timestamps=timestamps,
    #         groupby=groupby,  # type: ignore[arg-type]
    #     )
    #     response["statistics"] = convert_numpy_arrays_to_lists(series_statistics)

    if analysis.value is not None:
        photovoltaic_performance_report = summarise_photovoltaic_performance(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            surface_orientation=True if surface_orientation else False,
            surface_tilt=True if surface_tilt else False,
            dictionary=photovoltaic_power_output_series.components,
            timestamps=timestamps,
            frequency=frequency,
            analysis=analysis,
        )
        response[PHOTOVOLTAIC_PERFORMANCE_COLUMN_NAME] = photovoltaic_performance_report
        # finally
        header_key = 'Content-Disposition'
        header_value = "attachment; filename=" + f"{PHOTOVOLTAIC_PERFORMANCE_ANALYSIS_OUTPUT_FILENAME}.json"
        headers = {
            header_key: header_value, 
        }
        # return Response(
        #     orjson.dumps(response, option=orjson.OPT_SERIALIZE_NUMPY), headers=headers, media_type="application/json"
        # )
        # return ORJSONResponse([response], headers=headers, media_type="application/json")

    if metadata:
        response['Metadata'] = get_metadata(request=request)

    if quick_response_code.value != QuickResponseCode.NoneValue:
        quick_response = generate_quick_response_code(
            dictionary=photovoltaic_power_output_series.components,
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            surface_orientation=True,
            surface_tilt=True,
            timestamps=timestamps,
            rounding_places=ROUNDING_PLACES_DEFAULT,
            output_type=quick_response_code,
        )
        if quick_response_code.value == QuickResponseCode.Base64:
            response["QR"] = (f"data:image/png;base64,{quick_response}")
        elif quick_response_code.value == QuickResponseCode.Image:
            from io import BytesIO
            buffer = BytesIO()
            image = quick_response.make_image()
            image.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
            return Response(content=image_bytes, media_type="image/png")
        else:
            return JSONResponse(content={"message": "No QR code generated."})


    # return Response(
    #     orjson.dumps(response, option=orjson.OPT_SERIALIZE_NUMPY), headers=headers, media_type="application/json"
    # )
    return ORJSONResponse([response], headers=headers, media_type="application/json")

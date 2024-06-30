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
from pvgisprototype.api.power.broadband import (
    calculate_photovoltaic_power_output_series,
)
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.performance.report import summarise_photovoltaic_performance
from pvgisprototype.api.quick_response_code import generate_quick_response_code
from pvgisprototype.api.quick_response_code import QuickResponseCode
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.constants import (
    DEGREES,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    METADATA_FLAG_DEFAULT,
    NOT_AVAILABLE,
    PEAK_POWER_DEFAULT,
    PHOTOVOLTAIC_PERFORMANCE_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_OUTPUT_FILENAME,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SYSTEM_EFFICIENCY_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.web_api.dependencies import (
    fastapi_dependable_frequency,
    fastapi_dependable_latitude,
    fastapi_dependable_longitude,
    fastapi_dependable_surface_orientation,
    fastapi_dependable_surface_tilt,
    fastapi_dependable_timestamps,
    fastapi_dependable_timezone,
    fastapi_dependable_verbose,
    fastapi_dependable_fingerprint,
)
from pvgisprototype.web_api.fastapi_parameters import (
    fastapi_query_analysis,
    fastapi_query_csv,
    fastapi_query_elevation,
    fastapi_query_end_time,
    fastapi_query_peak_power,
    fastapi_query_periods,
    fastapi_query_photovoltaic_module_model,
    fastapi_query_power_model,
    fastapi_query_quick_response_code,
    fastapi_query_index,
    fastapi_query_quiet,
    fastapi_query_start_time,
    fastapi_query_system_efficiency,
)
from pvgisprototype.web_api.schemas import AnalysisLevel, Frequency, Timezone


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
    timestamps: Annotated[DatetimeIndex | None, fastapi_dependable_timestamps] = None,
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

    <span style="color:red"> <ins>**This Application Is a Feasibility Study**</ins></span>
    **limited to** longitudes ranging in [`7.5`, `10`] and latitudes in [`45`, `47.5`].

    # Features

    - A symbol nomenclature for easy identification of quantities, units, and more -- see [Symbols](https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/cli/symbols/)
    - Arbitrary time series supported by [Pandas' DatetimeIndex](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html) 
    - Valid time zone identifiers from [the IANA Time Zone Database](https://www.iana.org/time-zones)
    - Surface position optimisation supported by [SciPy](https://docs.scipy.org/doc/scipy/reference/optimize.html) (**pending integration**)
    - Get from simple to detailed output in form of **JSON**, **CSV** and **Excel** (the latter **pending implementation**)
    - Share a **QR-Code** with a summary of the analysis
    - **Fingerprint** your analysis
    - Document your analysis including all **input metadata**

    ## **Important Notes**

    - The default time, if not given, regardless of the `frequency` is
      `00:00:00`. It is then expected to get `0` incoming solar irradiance and
      subsequently photovoltaic power/energy output.

    - Of the four parameters `start_time`, `end_time`, `periods`, and
      `frequency`, exactly three must be specified. If `frequency` is omitted,
      the resulting timestamps (a Pandas `DatetimeIndex` object)
      will have `periods` linearly spaced elements between `start_time` and
      `end_time` (closed on both sides). Learn more about frequency strings at
      [Offset aliases](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases).

    ## Need more control ?

    In the `/performance/advanced` endpoint you may find :

    - Optional algorithms for solar timing, positioning and the estimation of the solar incidence angle
    - Disable atmospheric refraction for solar positioning
    - Simpler power-rating model as well as module temperature model
    - and more

    # Algorithms & Models

    - Solar radiation model by Hofierka, 2002
    - Photovoltaic efficiency coefficients by ESTI, C2, JRC, European Commission
    - Solar positioning based on NOAA's solar geometry equations
    - Reflectivity effect as a function of the solar incidence angle by Martin and Ruiz, 2005
    - Spectal mismatch effect by Huld, 2011
    - Overall system efficiency pre-set to 0.86, in other words 14% of loss for material degradation, aging, etc.

    # Input data

    This function consumes internally :
    
    - time series data limited to the period **2005** - **2023**.
    - solar irradiance from the [SARAH3 climate records](https://wui.cmsaf.eu/safira/action/viewDoiDetails?acronym=SARAH_V003)
    - temperature and wind speed estimations from [ERA5 Reanalysis](https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5) collection
    - spectral effect factor time series (Huld, 2011) _for the reference year 2013_

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

        header:list = []
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
                dictionary[key] = np.full(len(timestamps), value) # type: ignore
            if isinstance(value, str):
                dictionary[key] = np.full(len(timestamps), str(value)) # type: ignore
        
        # Zip series and timestamps
        zipped_series = zip(*dictionary.values())
        zipped_data = zip(timestamps, zipped_series) # type: ignore
        
        rows = []
        for idx, (timestamp, values) in enumerate(zipped_data):
            row = []
            if index:
                row.append(idx)
            if longitude and latitude:
                row.extend([longitude, latitude]) # type: ignore
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
    headers = {
                "Content-Disposition": f'attachment; filename="{PHOTOVOLTAIC_POWER_OUTPUT_FILENAME}.json"'
            }

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
            
    if analysis.value != AnalysisLevel.NoneValue:
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
            image = quick_response.make_image() # type: ignore
            image.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
            return Response(content=image_bytes, media_type="image/png")
        else:
            return JSONResponse(content={"message": "No QR code generated."})


    # return Response(
    #     orjson.dumps(response, option=orjson.OPT_SERIALIZE_NUMPY), headers=headers, media_type="application/json"
    # )
    return ORJSONResponse(response, headers=headers, media_type="application/json")

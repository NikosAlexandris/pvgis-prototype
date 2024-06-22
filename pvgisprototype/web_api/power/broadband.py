import math
from pathlib import Path
from typing import Annotated, Any

import numpy as np
import orjson
from fastapi.responses import Response
from pandas import to_datetime

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
from pvgisprototype.constants import (
    EFFICIENCY_FACTOR_DEFAULT,
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
    fastapi_dependable_solar_incidence_models,
    fastapi_dependable_solar_position_models,
    fastapi_dependable_spectral_factor_series,
    fastapi_dependable_surface_orientation,
    fastapi_dependable_surface_orientation_list,
    fastapi_dependable_surface_tilt,
    fastapi_dependable_surface_tilt_list,
    fastapi_dependable_timestamps,
    fastapi_dependable_timezone,
)
from pvgisprototype.web_api.fastapi_parameters import (
    fastapi_query_efficiency,
    fastapi_query_module_temperature_algorithm,
    fastapi_query_radiation_cutoff_threshold,
    fastapi_query_albedo,
    fastapi_query_analysis,
    fastapi_query_apply_atmospheric_refraction,
    fastapi_query_apply_reflectivity_factor,
    fastapi_query_csv,
    fastapi_query_eccentricity_correction_factor,
    fastapi_query_elevation,
    fastapi_query_end_time,
    fastapi_query_fingerprint,
    fastapi_query_in_memory,
    fastapi_query_mask_and_scale,
    fastapi_query_neighbor_lookup,
    fastapi_query_peak_power,
    fastapi_query_perigee_offset,
    fastapi_query_periods,
    fastapi_query_photovoltaic_module_model,
    fastapi_query_power_model,
    fastapi_query_quick_response_code,
    fastapi_query_quiet,
    fastapi_query_solar_constant,
    fastapi_query_solar_time_model,
    fastapi_query_start_time,
    fastapi_query_statistics,
    fastapi_query_system_efficiency,
    fastapi_query_tolerance,
    fastapi_query_verbose,
    fastapi_query_zero_negative_solar_incidence_angle,
)
from pvgisprototype.web_api.schemas import AngleOutputUnit, Frequency, GroupBy, Timezone
from pvgisprototype.web_api.dependencies import fastapi_dependable_verbose, fastapi_dependable_quite, fastapi_dependable_fingerprint
from pvgisprototype.constants import QUICK_RESPONSE_CODE_FLAG_DEFAULT

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


def plot_monthly_means(statistics: dict, figure_name: str = "monthly_means_plot"):
    """
    Plot the monthly means series and save the plot to a file.

    Parameters:
        statistics (dict): The statistics dictionary containing "Monthly means".
        figure_name (str): The base name for the output plot file.

    Returns:
        str: The path to the saved plot file.
    """
    import matplotlib.pyplot as plt

    monthly_means = statistics["Monthly means"]
    months = np.arange(1, 13)  # Assuming the data covers 12 months

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(months, monthly_means, marker="o", linestyle="-", color="b")
    plt.title("Monthly Means of Photovoltaic Power Output")
    plt.xlabel("Month")
    plt.ylabel("Mean Output")
    plt.xticks(months)
    plt.grid(True)

    # Save the plot to a file
    output_file = f"{figure_name}.png"
    plt.savefig(output_file)
    plt.close()  # Close the plot to free up memory

    return output_file


async def get_photovoltaic_power_series_advanced(
    longitude: Annotated[float, fastapi_dependable_longitude] = 8.628,
    latitude: Annotated[float, fastapi_dependable_latitude] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214.0,
    surface_orientation: Annotated[
        float, fastapi_dependable_surface_orientation
    ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[
        float, fastapi_dependable_surface_tilt
    ] = SURFACE_TILT_DEFAULT,
    timestamps: Annotated[str | None, fastapi_dependable_timestamps] = None,
    start_time: Annotated[str | None, fastapi_query_start_time] = None,
    periods: Annotated[str | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hour,
    end_time: Annotated[str | None, fastapi_query_end_time] = None,
    timezone: Annotated[Timezone, fastapi_dependable_timezone] = Timezone.UTC,  # type: ignore[attr-defined]
    # global_horizontal_irradiance: Annotated[Optional[Path], fastapi_query_global_horizontal_irradiance] = None,
    # direct_horizontal_irradiance: Annotated[Optional[Path], fastapi_query_direct_horizontal_irradiance] = None,
    # temperature_series: Annotated[float, fastapi_query_temperature_series] = TEMPERATURE_DEFAULT,
    # temperature_series: Optional[TemperatureSeries] = fastapi_dependable_temperature_series,
    # wind_speed_series: Annotated[float, fastapi_query_wind_speed_series] = WIND_SPEED_DEFAULT,
    # wind_speed_series: Optional[WindSpeedSeries] = fastapi_dependable_wind_speed_series,
    spectral_factor_series: Annotated[
        SpectralFactorSeries, fastapi_dependable_spectral_factor_series
    ] = None,
    neighbor_lookup: Annotated[
        MethodForInexactMatches, fastapi_query_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float, fastapi_query_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, fastapi_query_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, fastapi_query_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    linke_turbidity_factor_series: Annotated[
        float | LinkeTurbidityFactor, fastapi_dependable_linke_turbidity_factor_series
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: Annotated[
        bool, fastapi_query_apply_atmospheric_refraction
    ] = True,
    refracted_solar_zenith: Annotated[
        float, fastapi_dependable_refracted_solar_zenith
    ] = math.degrees(REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT),
    albedo: Annotated[float, fastapi_query_albedo] = ALBEDO_DEFAULT,
    apply_reflectivity_factor: Annotated[
        bool, fastapi_query_apply_reflectivity_factor
    ] = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: Annotated[
        SolarPositionModel, fastapi_dependable_solar_position_models
    ] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[
        SolarIncidenceModel, fastapi_dependable_solar_incidence_models
    ] = SolarIncidenceModel.iqbal,
    zero_negative_solar_incidence_angle: Annotated[
        bool, fastapi_query_zero_negative_solar_incidence_angle
    ] = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: Annotated[
        SolarTimeModel, fastapi_query_solar_time_model
    ] = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: Annotated[float, fastapi_query_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, fastapi_query_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[
        float, fastapi_query_eccentricity_correction_factor
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_dependable_angle_output_units
    ] = AngleOutputUnit.RADIANS,
    photovoltaic_module: Annotated[
        PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model
    ] = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    peak_power: Annotated[float, fastapi_query_peak_power] = 1.0,  # FIXME ADD CONSTANT?
    system_efficiency: Annotated[
        float, fastapi_query_system_efficiency
    ] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[
        PhotovoltaicModulePerformanceModel, fastapi_query_power_model
    ] = PhotovoltaicModulePerformanceModel.king,
    radiation_cutoff_threshold: Annotated[
        float, fastapi_query_radiation_cutoff_threshold
    ] = RADIATION_CUTOFF_THRESHHOLD,
    temperature_model: Annotated[
        ModuleTemperatureAlgorithm, fastapi_query_module_temperature_algorithm
    ] = ModuleTemperatureAlgorithm.faiman,
    efficiency: Annotated[float | None, fastapi_query_efficiency] = EFFICIENCY_FACTOR_DEFAULT,
    # dtype: str = DATA_TYPE_DEFAULT,
    # array_backend: str = ARRAY_BACKEND_DEFAULT,
    # multi_thread: bool = MULTI_THREAD_FLAG_DEFAULT,
    # uniplot: Annotated[bool, fastapi_query_uniplot] = UNIPLOT_FLAG_DEFAULT,
    # terminal_width_fraction: Annotated[float, fastapi_query_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, fastapi_dependable_verbose] = VERBOSE_LEVEL_DEFAULT,
    # log: Annotated[int, fastapi_query_log] = LOG_LEVEL_DEFAULT,
    # profile: Annotated[bool, fastapi_query_profiling] = cPROFILE_FLAG_DEFAULT,
    statistics: Annotated[bool, fastapi_query_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[GroupBy, fastapi_dependable_groupby] = GroupBy.N,
    csv: Annotated[bool, fastapi_query_csv] = False,
    quiet: Annotated[bool, fastapi_dependable_quite] = QUIET_FLAG_DEFAULT,
    fingerprint: Annotated[bool, fastapi_dependable_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    analysis: Annotated[bool, fastapi_query_analysis] = ANALYSIS_FLAG_DEFAULT,
    quick_response_code: Annotated[bool, fastapi_query_quick_response_code] = QUICK_RESPONSE_CODE_FLAG_DEFAULT,
):
    """Estimate the photovoltaic power output for a solar surface.

    Estimate the photovoltaic power for a solar surface over a time series or
    an arbitrarily aggregated energy production of a PV system connected to the
    electricity grid (without battery storage) based on broadband solar
    irradiance, ambient temperature and wind speed.
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
        spectral_factor_series=spectral_factor_series,
        temperature_series=Path(
            "era5_t2m_over_esti_jrc.nc"
        ),  # FIXME This hardwritten path will be replaced
        wind_speed_series=Path(
            "era5_ws2m_over_esti_jrc.nc"
        ),  # FIXME This hardwritten path will be replaced
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        in_memory=in_memory,
        linke_turbidity_factor_series=linke_turbidity_factor_series,  # LinkeTurbidityFactor = LinkeTurbidityFactor(value = LINKE_TURBIDITY_TIME_SERIES_DEFAULT),
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        albedo=albedo,
        apply_reflectivity_factor=apply_reflectivity_factor,
        solar_position_model=solar_position_model,
        solar_incidence_model=solar_incidence_model,
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        solar_time_model=solar_time_model,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
        photovoltaic_module=photovoltaic_module,
        peak_power=peak_power,
        system_efficiency=system_efficiency,
        power_model=power_model,
        radiation_cutoff_threshold=radiation_cutoff_threshold,
        temperature_model=temperature_model,
        efficiency=efficiency,
        # dtype=dtype,
        # array_backend=array_backend,
        # multi_thread=multi_thread,
        verbose=verbose,
        log=verbose,
        fingerprint=fingerprint,
        # profile=profile,
    )

    if csv:
        from datetime import datetime

        from fastapi.responses import StreamingResponse

        streaming_data = [
            (str(timestamp), photovoltaic_power)
            for timestamp, photovoltaic_power in zip(
                timestamps.tolist(), photovoltaic_power_output_series.value.tolist()  # type: ignore
            )
        ]
        filename = f"photovoltaic_power_output_{photovoltaic_power_output_series.components[FINGERPRINT_COLUMN_NAME]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        csv_content = ",".join(["Timestamp", "Photovoltaic Power"]) + "\n"
        csv_content += (
            "\n".join(
                [
                    ",".join([timestamp, str(photovoltaic_power)])
                    for timestamp, photovoltaic_power in streaming_data
                ]
            )
            + "\n"
        )
        response_csv = StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
        return response_csv

    if quick_response_code:
        from io import BytesIO
        from pvgisprototype.cli.qr import print_quick_response_code

        image = print_quick_response_code(
            dictionary=photovoltaic_power_output_series.components,
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            surface_orientation=True,
            surface_tilt=True,
            timestamps=timestamps,
            rounding_places=ROUNDING_PLACES_DEFAULT,
            image=True,
        )

        buffer = BytesIO()
        image.save(buffer, format="PNG")  # type: ignore
        image_bytes = buffer.getvalue()
        #import base64
        #image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        #response["qr"] = (
        #    f"data:image/png;base64,{image_base64}"  # This way the image is returned in the JSON as a server link
        #)

        return Response(content=image_bytes, media_type="image/png")

    response = {}

    if fingerprint:
        response["fingerprint"] = photovoltaic_power_output_series.components[
            FINGERPRINT_COLUMN_NAME
        ]

    if statistics:
        from pvgisprototype.api.series.statistics import calculate_series_statistics

        series_statistics = calculate_series_statistics(
            data_array=photovoltaic_power_output_series.value,
            timestamps=timestamps,
            groupby=groupby,  # type: ignore[arg-type]
        )
        response["statistics"] = convert_numpy_arrays_to_lists(series_statistics)


    if analysis:
        photovoltaic_performance_report = summarise_photovoltaic_performance(
            dictionary=photovoltaic_power_output_series.components,
                timestamps=timestamps,
                frequency=frequency,
                )
        response["analysis"] = photovoltaic_performance_report

    if not quiet:
        if verbose > 0:
            response = convert_numpy_arrays_to_lists(
                photovoltaic_power_output_series.components
            )
        else:
            response["results"] = {
                "Photovoltaic power output series": photovoltaic_power_output_series.value,
            }

    # finally
    headers = {
        "Content-Disposition": 'attachment; filename="pvgis_photovoltaic_power_series.json"'
    }
    return Response(
        orjson.dumps(response, option=orjson.OPT_SERIALIZE_NUMPY), headers=headers, media_type="application/json"
    )


async def get_photovoltaic_power_series(
    longitude: Annotated[float, fastapi_dependable_longitude] = 8.628,
    latitude: Annotated[float, fastapi_dependable_latitude] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214.0,
    surface_orientation: Annotated[ float, fastapi_dependable_surface_orientation ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[ float, fastapi_dependable_surface_tilt ] = SURFACE_TILT_DEFAULT,
    timestamps: Annotated[str | None, fastapi_dependable_timestamps] = None,
    start_time: Annotated[str | None, fastapi_query_start_time] = None,
    periods: Annotated[str | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hour,
    end_time: Annotated[str | None, fastapi_query_end_time] = None,
    timezone: Annotated[Timezone, fastapi_dependable_timezone] = Timezone.UTC,  # type: ignore[attr-defined]
    photovoltaic_module: Annotated[ PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model ] = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    system_efficiency: Annotated[ float, fastapi_query_system_efficiency ] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[ PhotovoltaicModulePerformanceModel, fastapi_query_power_model ] = PhotovoltaicModulePerformanceModel.king,
    peak_power: Annotated[float, fastapi_query_peak_power] = 1.0,  # FIXME ADD CONSTANT?
    statistics: Annotated[bool, fastapi_query_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[GroupBy, fastapi_dependable_groupby] = GroupBy.N,
    csv: Annotated[bool, fastapi_query_csv] = False,
    verbose: Annotated[int, fastapi_dependable_verbose] = VERBOSE_LEVEL_DEFAULT,
    quiet: Annotated[bool, fastapi_dependable_quite] = QUIET_FLAG_DEFAULT,
    fingerprint: Annotated[bool, fastapi_dependable_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    analysis: Annotated[bool, fastapi_query_analysis] = ANALYSIS_FLAG_DEFAULT,
    quick_response_code: Annotated[bool, fastapi_query_quick_response_code] = QUICK_RESPONSE_CODE_FLAG_DEFAULT,
):
    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        global_horizontal_irradiance=Path(
            "sarah2_sis_over_esti_jrc.nc"
        ),  # FIXME This hardwritten path will be replaced
        direct_horizontal_irradiance=Path(
            "sarah2_sid_over_esti_jrc.nc"
        ),  # FIXME This hardwritten path will be replaced
        temperature_series=Path(
            "era5_t2m_over_esti_jrc.nc"
        ),  # FIXME This hardwritten path will be replaced
        wind_speed_series=Path(
            "era5_ws2m_over_esti_jrc.nc"
        ),  # FIXME This hardwritten path will be replaced
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        photovoltaic_module=photovoltaic_module,
        system_efficiency=system_efficiency,
        power_model=power_model,
        peak_power=peak_power,
        verbose=verbose,
        fingerprint=fingerprint,
    )
    if csv:
        from datetime import datetime

        from fastapi.responses import StreamingResponse

        streaming_data = [(str(timestamp), photovoltaic_power) for timestamp, photovoltaic_power in zip(timestamps.tolist(), photovoltaic_power_output_series.value.tolist())]  # type: ignore
        filename = f"photovoltaic_power_output_{photovoltaic_power_output_series.components[FINGERPRINT_COLUMN_NAME]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        csv_content = ",".join(["Timestamp", "Photovoltaic Power"]) + "\n"
        csv_content += (
            "\n".join(
                [
                    ",".join([timestamp, str(photovoltaic_power)])
                    for timestamp, photovoltaic_power in streaming_data
                ]
            )
            + "\n"
        )
        response_csv = StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
        return response_csv

    response = {}
    if not quiet:

        if verbose > 0:
            response = convert_numpy_arrays_to_lists(
                photovoltaic_power_output_series.components
            )
        else:
            response = {
               "Photovoltaic power output series": photovoltaic_power_output_series.value,
            }

    if fingerprint:
        response["fingerprint"] = photovoltaic_power_output_series.components[
            FINGERPRINT_COLUMN_NAME
        ]

    if statistics:
        from pvgisprototype.api.series.statistics import calculate_series_statistics

        series_statistics = calculate_series_statistics(
            data_array=photovoltaic_power_output_series.value,
            timestamps=timestamps,
            groupby=groupby,  # type: ignore[arg-type]
        )
        response["statistics"] = convert_numpy_arrays_to_lists(series_statistics)

    if analysis:
        photovoltaic_performance_report = summarise_photovoltaic_performance(
            dictionary=photovoltaic_power_output_series.components,
                timestamps=timestamps,
                frequency=frequency,
                )
        response["analysis"] = photovoltaic_performance_report
        # finally
        headers = {
            "Content-Disposition": 'attachment; filename="photovoltaic_performance_analysis.json"'
        }
        return Response(
            orjson.dumps(response, option=orjson.OPT_SERIALIZE_NUMPY), headers=headers, media_type="application/json"
        )

    if quick_response_code:
        import base64
        from io import BytesIO

        from pvgisprototype.cli.qr import print_quick_response_code

        image = print_quick_response_code(
            dictionary=photovoltaic_power_output_series.components,
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            surface_orientation=True,
            surface_tilt=True,
            timestamps=timestamps,
            rounding_places=ROUNDING_PLACES_DEFAULT,
            image=True,
        )
        buffer = BytesIO()
        image.save(buffer, format="PNG")  # type: ignore
        image_bytes = buffer.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        response["QR"] = (
            f"data:image/png;base64,{image_base64}"  # This way the image is returned in the JSON as a server link
        )
        #image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        #response["qr"] = (
        #    f"data:image/png;base64,{image_base64}"  # This way the image is returned in the JSON as a server link
        #)

        return Response(content=image_bytes, media_type="image/png")

    # finally
    headers = {
        "Content-Disposition": 'attachment; filename="pvgis_photovoltaic_power_series.json"'
    }
    return Response(
        orjson.dumps(response, option=orjson.OPT_SERIALIZE_NUMPY), headers=headers, media_type="application/json"
    )


async def get_photovoltaic_power_series_monthly_average(
    longitude: Annotated[float, fastapi_dependable_longitude] = 8.628,
    latitude: Annotated[float, fastapi_dependable_latitude] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214.0,
    surface_orientation: Annotated[
        float, fastapi_dependable_surface_orientation
    ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[
        float, fastapi_dependable_surface_tilt
    ] = SURFACE_TILT_DEFAULT,
    timestamps: Annotated[str | None, fastapi_dependable_timestamps] = None,
    start_time: Annotated[str | None, fastapi_query_start_time] = None,
    periods: Annotated[str | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hour,
    end_time: Annotated[str | None, fastapi_query_end_time] = None,
    timezone: Annotated[Timezone, fastapi_dependable_timezone] = Timezone.UTC,  # type: ignore[attr-defined]
    spectral_factor_series: Annotated[
        SpectralFactorSeries, fastapi_dependable_spectral_factor_series
    ] = None,
    photovoltaic_module: Annotated[
        PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model
    ] = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    system_efficiency: Annotated[
        float, fastapi_query_system_efficiency
    ] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[
        PhotovoltaicModulePerformanceModel, fastapi_query_power_model
    ] = PhotovoltaicModulePerformanceModel.king,
    csv: bool = False,
    plot_statistics: bool = False,
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, fastapi_query_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
):
    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        timestamps=timestamps,
        timezone=timezone,
        global_horizontal_irradiance=Path("sarah2_sis_over_esti_jrc.nc"),
        direct_horizontal_irradiance=Path("sarah2_sid_over_esti_jrc.nc"),
        temperature_series=Path("era5_t2m_over_esti_jrc.nc"),
        wind_speed_series=Path("era5_ws2m_over_esti_jrc.nc"),
        spectral_factor_series=spectral_factor_series,
        photovoltaic_module=photovoltaic_module,
        system_efficiency=system_efficiency,
        power_model=power_model,
        efficiency=EFFICIENCY_FACTOR_DEFAULT,
        verbose=verbose,
        fingerprint=fingerprint,
    )
    if csv:
        from datetime import datetime

        from fastapi.responses import StreamingResponse

        streaming_data = [
            (str(timestamp), photovoltaic_power)
            for timestamp, photovoltaic_power in zip(
                timestamps.tolist(), photovoltaic_power_output_series.value.tolist()  # type: ignore
            )
        ]
        filename = f"photovoltaic_power_output_{photovoltaic_power_output_series.components[FINGERPRINT_COLUMN_NAME]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        csv_content = ",".join(["Timestamp", "Photovoltaic Power"]) + "\n"
        csv_content += (
            "\n".join(
                [
                    ",".join([timestamp, str(photovoltaic_power)])
                    for timestamp, photovoltaic_power in streaming_data
                ]
            )
            + "\n"
        )
        response_csv = StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
        return response_csv

    response = {}
    statistics = True
    if statistics:
        from pvgisprototype.api.series.statistics import calculate_series_statistics

        series_statistics = calculate_series_statistics(
            data_array=photovoltaic_power_output_series.value,
            timestamps=timestamps,
            groupby="M",
        )
        response["statistics"] = convert_numpy_arrays_to_lists(series_statistics)

        if plot_statistics:
            plot_file = plot_monthly_means(series_statistics, "monthly_means_plot")

            from fastapi.responses import FileResponse

            return FileResponse(
                path=plot_file, filename=Path(plot_file).name, media_type="image/png"
            )

    headers = {
        "Content-Disposition": 'attachment; filename="pvgis_photovoltaic_power_series.json"'
    }
    return Response(
        orjson.dumps(response, option=orjson.OPT_SERIALIZE_NUMPY), headers=headers, media_type="application/json"
    )


async def get_photovoltaic_power_output_series_multi(
    longitude: Annotated[float, fastapi_dependable_longitude] = 8.628,
    latitude: Annotated[float, fastapi_dependable_latitude] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214.0,
    surface_orientation: Annotated[
        list[float], fastapi_dependable_surface_orientation_list
    ] = [float(SURFACE_ORIENTATION_DEFAULT)],
    surface_tilt: Annotated[list[float], fastapi_dependable_surface_tilt_list] = [
        float(SURFACE_TILT_DEFAULT)
    ],
    timestamps: Annotated[str | None, fastapi_dependable_timestamps] = None,
    start_time: Annotated[str | None, fastapi_query_start_time] = None,
    periods: Annotated[str | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hour,
    end_time: Annotated[str | None, fastapi_query_end_time] = None,
    timezone: Annotated[Timezone, fastapi_dependable_timezone] = Timezone.UTC,  # type: ignore[attr-defined]
    spectral_factor_series: Annotated[
        SpectralFactorSeries, fastapi_dependable_spectral_factor_series
    ] = None,
    neighbor_lookup: Annotated[
        MethodForInexactMatches, fastapi_query_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float, fastapi_query_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, fastapi_query_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, fastapi_query_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    linke_turbidity_factor_series: Annotated[
        float | LinkeTurbidityFactor, fastapi_dependable_linke_turbidity_factor_series
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: Annotated[
        bool, fastapi_query_apply_atmospheric_refraction
    ] = True,
    refracted_solar_zenith: Annotated[
        float, fastapi_dependable_refracted_solar_zenith
    ] = math.degrees(REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT),
    albedo: Annotated[float, fastapi_query_albedo] = ALBEDO_DEFAULT,
    apply_reflectivity_factor: Annotated[
        bool, fastapi_query_apply_reflectivity_factor
    ] = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: Annotated[
        SolarPositionModel, fastapi_dependable_solar_position_models
    ] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[
        SolarIncidenceModel, fastapi_dependable_solar_incidence_models
    ] = SolarIncidenceModel.iqbal,
    zero_negative_solar_incidence_angle: Annotated[
        bool, fastapi_query_zero_negative_solar_incidence_angle
    ] = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: Annotated[
        SolarTimeModel, fastapi_query_solar_time_model
    ] = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: Annotated[float, fastapi_query_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, fastapi_query_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[
        float, fastapi_query_eccentricity_correction_factor
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_dependable_angle_output_units
    ] = AngleOutputUnit.RADIANS,
    photovoltaic_module: Annotated[
        PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model
    ] = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    peak_power: Annotated[float, fastapi_query_peak_power] = 1.0,  # FIXME ADD CONSTANT?
    system_efficiency: Annotated[
        float, fastapi_query_system_efficiency
    ] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[
        PhotovoltaicModulePerformanceModel, fastapi_query_power_model
    ] = PhotovoltaicModulePerformanceModel.king,
    # radiation_cutoff_threshold: Annotated[float, fastapi_query_radiation_cutoff_threshold] = RADIATION_CUTOFF_THRESHHOLD,
    temperature_model: Annotated[
        ModuleTemperatureAlgorithm, fastapi_query_module_temperature_algorithm
    ] = ModuleTemperatureAlgorithm.faiman,
    efficiency: Annotated[float | None, fastapi_query_efficiency] = EFFICIENCY_FACTOR_DEFAULT,
    statistics: Annotated[bool, fastapi_query_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[GroupBy, fastapi_dependable_groupby] = GroupBy.N,
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
    csv: Annotated[bool, fastapi_query_csv] = False,
    quiet: Annotated[bool, fastapi_query_quiet] = QUIET_FLAG_DEFAULT,
    fingerprint: Annotated[bool, fastapi_query_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    # analysis: Annotated[bool, fastapi_query_analysis] = ANALYSIS_FLAG_DEFAULT,
    # quick_response_code: Annotated[bool, fastapi_query_quick_response_code] = False,
    # multi_thread: bool = MULTI_THREAD_FLAG_DEFAULT,
):

    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series_from_multiple_surfaces(
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
        spectral_factor_series=spectral_factor_series,
        temperature_series=Path(
            "era5_t2m_over_esti_jrc.nc"
        ),  # FIXME This hardwritten path will be replaced
        wind_speed_series=Path(
            "era5_ws2m_over_esti_jrc.nc"
        ),  # FIXME This hardwritten path will be replaced
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        in_memory=in_memory,
        linke_turbidity_factor_series=linke_turbidity_factor_series,  # LinkeTurbidityFactor = LinkeTurbidityFactor(value = LINKE_TURBIDITY_TIME_SERIES_DEFAULT),
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        albedo=albedo,
        apply_reflectivity_factor=apply_reflectivity_factor,
        solar_position_model=solar_position_model,
        solar_incidence_model=solar_incidence_model,
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        solar_time_model=solar_time_model,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
        photovoltaic_module=photovoltaic_module,
        # peak_power=peak_power,
        system_efficiency=system_efficiency,
        power_model=power_model,
        # radiation_cutoff_threshold=radiation_cutoff_threshold,
        temperature_model=temperature_model,
        efficiency=efficiency,
        verbose=verbose,
        log=verbose,
        fingerprint=True,
    )

    if not quiet:

        if verbose > 0:
            response = convert_numpy_arrays_to_lists(
                photovoltaic_power_output_series.components
            )
        else:
            response = {
                "Photovoltaic power output series": photovoltaic_power_output_series.value,
            }

    if fingerprint:
        response["fingerprint"] = photovoltaic_power_output_series.components[
            FINGERPRINT_COLUMN_NAME
        ]

    if statistics:
        from pvgisprototype.api.series.statistics import calculate_series_statistics

        series_statistics = calculate_series_statistics(
            data_array=photovoltaic_power_output_series.value,
            timestamps=timestamps,
            groupby=groupby,  # type: ignore[arg-type]
        )
        response["statistics"] = convert_numpy_arrays_to_lists(series_statistics)

    if csv:
        from datetime import datetime

        from fastapi.responses import StreamingResponse

        streaming_data = [
            (str(timestamp), photovoltaic_power)
            for timestamp, photovoltaic_power in zip(
                timestamps.tolist(), photovoltaic_power_output_series.value.tolist()  # type: ignore
            )
        ]
        filename = f"photovoltaic_power_output_{photovoltaic_power_output_series.components[FINGERPRINT_COLUMN_NAME]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        csv_content = ",".join(["Timestamp", "Photovoltaic Power"]) + "\n"
        csv_content += (
            "\n".join(
                [
                    ",".join([timestamp, str(photovoltaic_power)])
                    for timestamp, photovoltaic_power in streaming_data
                ]
            )
            + "\n"
        )

        response_csv = StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

        return response_csv

    headers = {"Content-Disposition": 'attachment; filename="data.json"'}
    return Response(
        orjson.dumps(response, option=orjson.OPT_SERIALIZE_NUMPY), headers=headers, media_type="application/json"
    )

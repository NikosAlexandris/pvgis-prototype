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
from pvgisprototype.api.quick_response_code import QuickResponseCode
from pvgisprototype.constants import (
    EFFICIENCY_FACTOR_DEFAULT,
    PEAK_POWER_DEFAULT,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    RADIATION_CUTOFF_THRESHHOLD,
    ALBEDO_DEFAULT,
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
    fastapi_query_temperature_model,
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
from pvgisprototype.web_api.schemas import AnalysisLevel
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.constants import PHOTOVOLTAIC_POWER_OUTPUT_FILENAME
from pvgisprototype.api.quick_response_code import generate_quick_response_code
from pvgisprototype.constants import PHOTOVOLTAIC_PERFORMANCE_COLUMN_NAME
from fastapi.responses import ORJSONResponse
from pvgisprototype.api.series.statistics import calculate_series_statistics
from pvgisprototype.api.surface.parameter_models import SurfacePositionOptimizerMode
from pvgisprototype.web_api.dependencies import fastapi_dependable_optimise_surface_position


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
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hourly,
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
    peak_power: Annotated[float, fastapi_query_peak_power] = PEAK_POWER_DEFAULT,
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
        ModuleTemperatureAlgorithm, fastapi_query_temperature_model,
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
    groupby: Annotated[GroupBy, fastapi_dependable_groupby] = GroupBy.NoneValue,
    csv: Annotated[str | None, fastapi_query_csv] = None,
    quiet: Annotated[bool, fastapi_dependable_quite] = QUIET_FLAG_DEFAULT,
    fingerprint: Annotated[bool, fastapi_dependable_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    analysis: Annotated[AnalysisLevel, fastapi_query_analysis] = AnalysisLevel.Simple,
    quick_response_code: Annotated[QuickResponseCode, fastapi_query_quick_response_code] = QuickResponseCode.NoneValue,
    optimise_surface_position: Annotated[SurfacePositionOptimizerMode, fastapi_dependable_optimise_surface_position] = SurfacePositionOptimizerMode.NoneValue
):
    """Estimate the photovoltaic power output for a solar surface.

    Estimate the photovoltaic power for a solar surface over a time series or
    an arbitrarily aggregated energy production of a PV system connected to the
    electricity grid (without battery storage) based on broadband solar
    irradiance, ambient temperature and wind speed.
    """
    if optimise_surface_position:
        surface_orientation = optimise_surface_position['surface_orientation'].value # type: ignore
        surface_tilt = optimise_surface_position['surface_tilt'].value # type: ignore

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
    # -------------------------------------------------------------- Important
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    # ------------------------------------------------------------------------

    if csv:
        from fastapi.responses import StreamingResponse

        streaming_data = [
            (str(timestamp), photovoltaic_power)
            for timestamp, photovoltaic_power in zip(
                timestamps.tolist(), photovoltaic_power_output_series.value.tolist()  # type: ignore
            )
        ]

        if not csv.endswith(".csv"):
            filename = f"{csv}.csv"
        else:
            filename = csv
        
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
    
    response:dict = {}
    headers = {
                "Content-Disposition": f'attachment; filename="{PHOTOVOLTAIC_POWER_OUTPUT_FILENAME}.json"'
            }
    
    if fingerprint:
        response[FINGERPRINT_COLUMN_NAME] = photovoltaic_power_output_series.components[
            FINGERPRINT_COLUMN_NAME
        ]    
    
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

    if statistics:
        from pvgisprototype.api.series.statistics import calculate_series_statistics

        series_statistics = calculate_series_statistics(
            data_array=photovoltaic_power_output_series.value,
            timestamps=timestamps,
            groupby=groupby,  # type: ignore[arg-type]
        )
        response["Statistics"] = convert_numpy_arrays_to_lists(series_statistics)

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
    
    if not quiet:
        if verbose > 0:
            response = convert_numpy_arrays_to_lists(
                photovoltaic_power_output_series.components
            )
        else:
            response = {
                PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_output_series.value,
            }

    # finally
    return ORJSONResponse(response, headers=headers, media_type="application/json")


async def get_photovoltaic_power_series(
    longitude: Annotated[float, fastapi_dependable_longitude] = 8.628,
    latitude: Annotated[float, fastapi_dependable_latitude] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214.0,
    surface_orientation: Annotated[ float, fastapi_dependable_surface_orientation ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[ float, fastapi_dependable_surface_tilt ] = SURFACE_TILT_DEFAULT,
    timestamps: Annotated[str | None, fastapi_dependable_timestamps] = None,
    start_time: Annotated[str | None, fastapi_query_start_time] = None,
    periods: Annotated[str | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hourly,
    end_time: Annotated[str | None, fastapi_query_end_time] = None,
    timezone: Annotated[Timezone, fastapi_dependable_timezone] = Timezone.UTC,  # type: ignore[attr-defined]
    photovoltaic_module: Annotated[ PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model ] = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    system_efficiency: Annotated[ float, fastapi_query_system_efficiency ] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[PhotovoltaicModulePerformanceModel, fastapi_query_power_model ] = PhotovoltaicModulePerformanceModel.king,
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_dependable_angle_output_units
    ] = AngleOutputUnit.RADIANS,
    peak_power: Annotated[float, fastapi_query_peak_power] = PEAK_POWER_DEFAULT,
    statistics: Annotated[bool, fastapi_query_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[GroupBy, fastapi_dependable_groupby] = GroupBy.NoneValue,
    analysis: Annotated[AnalysisLevel, fastapi_query_analysis] = AnalysisLevel.Simple,
    csv: Annotated[str | None, fastapi_query_csv] = None,
    verbose: Annotated[int, fastapi_dependable_verbose] = VERBOSE_LEVEL_DEFAULT,
    quiet: Annotated[bool, fastapi_dependable_quite] = QUIET_FLAG_DEFAULT,
    fingerprint: Annotated[bool, fastapi_dependable_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    quick_response_code: Annotated[QuickResponseCode, fastapi_query_quick_response_code] = QuickResponseCode.NoneValue,
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
        angle_output_units=angle_output_units,
        power_model=power_model,
        peak_power=peak_power,
        verbose=verbose,
        fingerprint=fingerprint,
    )
    # -------------------------------------------------------------- Important
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    # ------------------------------------------------------------------------

    if csv:
        from fastapi.responses import StreamingResponse

        streaming_data = [
            (str(timestamp), photovoltaic_power)
            for timestamp, photovoltaic_power in zip(
                timestamps.tolist(), photovoltaic_power_output_series.value.tolist()  # type: ignore
            )
        ]

        if not csv.endswith(".csv"):
            filename = f"{csv}.csv"
        else:
            filename = csv
        
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
    
    response:dict = {}
    headers = {
                "Content-Disposition": f'attachment; filename="{PHOTOVOLTAIC_POWER_OUTPUT_FILENAME}.json"'
            }
    
    if fingerprint:
        response[FINGERPRINT_COLUMN_NAME] = photovoltaic_power_output_series.components[
            FINGERPRINT_COLUMN_NAME
        ]    
    
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


    if statistics:
        from pvgisprototype.api.series.statistics import calculate_series_statistics

        series_statistics = calculate_series_statistics(
            data_array=photovoltaic_power_output_series.value,
            timestamps=timestamps,
            groupby=groupby,  # type: ignore[arg-type]
        )
        response["Statistics"] = convert_numpy_arrays_to_lists(series_statistics)


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

    if not quiet:
        if verbose > 0:
            response = convert_numpy_arrays_to_lists(
                photovoltaic_power_output_series.components
            )
        else:
            response = {
                PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_output_series.value,
            }

    # finally
    return ORJSONResponse(response, headers=headers, media_type="application/json")


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
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hourly,
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
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_dependable_angle_output_units
    ] = AngleOutputUnit.RADIANS,
    csv: Annotated[str | None, fastapi_query_csv] = None,
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
        angle_output_units=angle_output_units,
        efficiency=EFFICIENCY_FACTOR_DEFAULT,
        verbose=verbose,
        fingerprint=fingerprint,
    )
    # -------------------------------------------------------------- Important
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    # ------------------------------------------------------------------------    
    if csv:
        from fastapi.responses import StreamingResponse

        streaming_data = [
            (str(timestamp), photovoltaic_power)
            for timestamp, photovoltaic_power in zip(
                timestamps.tolist(), photovoltaic_power_output_series.value.tolist()  # type: ignore
            )
        ]

        if not csv.endswith(".csv"):
            filename = f"{csv}.csv"
        else:
            filename = csv
        
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
    headers = {
        "Content-Disposition": 'attachment; filename="pvgis_photovoltaic_power_series.json"'
    }

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

    return ORJSONResponse(response, headers=headers, media_type="application/json")


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
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hourly,
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
    peak_power: Annotated[float, fastapi_query_peak_power] = PEAK_POWER_DEFAULT,
    system_efficiency: Annotated[
        float, fastapi_query_system_efficiency
    ] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[
        PhotovoltaicModulePerformanceModel, fastapi_query_power_model
    ] = PhotovoltaicModulePerformanceModel.king,
    # radiation_cutoff_threshold: Annotated[float, fastapi_query_radiation_cutoff_threshold] = RADIATION_CUTOFF_THRESHHOLD,
    temperature_model: Annotated[
        ModuleTemperatureAlgorithm, fastapi_query_temperature_model
    ] = ModuleTemperatureAlgorithm.faiman,
    efficiency: Annotated[float | None, fastapi_query_efficiency] = EFFICIENCY_FACTOR_DEFAULT,
    statistics: Annotated[bool, fastapi_query_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[GroupBy, fastapi_dependable_groupby] = GroupBy.NoneValue,
    csv: Annotated[str | None, fastapi_query_csv] = None,
    verbose: Annotated[int, fastapi_dependable_verbose] = VERBOSE_LEVEL_DEFAULT,
    quiet: Annotated[bool, fastapi_dependable_quite] = QUIET_FLAG_DEFAULT,
    fingerprint: Annotated[bool, fastapi_dependable_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    quick_response_code: Annotated[QuickResponseCode, fastapi_query_quick_response_code] = QuickResponseCode.NoneValue,
):
    """Calculate the total photovoltaic power/energy generated for a series of
    surface orientation and tilt angle pairs, optionally for various
    technologies, free-standing or building-integrated, at a specific location
    and a given period.

    # Features

    - Arbitrary time series supported by [Pandas' DatetimeIndex](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html) 
    - Optional algorithms for solar timing, positioning and the estimation of the solar incidence angle
    - Optionally Disable the atmospheric refraction for solar positioning
    - Optional power-rating models on top of optional module temperature models (pending integration of alternatives)
    - Get from simple to detailed output in form of **JSON**, **CSV** and **Excel** (the latter **pending implementation**)
    - Share a **QR-Code** with a summary of the analysis
    - **Fingerprint** your analysis
    - Document your analysis including all **input metadata**

    ## **Important Notes**

    - The function expects pairs of surface orientation
      (`surface_orientation`) and tilt (`surface_tilt`) angles, that is the
      number of requested orientation angles should equal the number of
      requested tilt angles.

    - The default time, if not given, regardless of the `frequency` is
      `00:00:00`. It is then expected to get `0` incoming solar irradiance and
      subsequently photovoltaic power/energy output.

    - Of the four parameters `start_time`, `end_time`, `periods`, and
      `frequency`, exactly three must be specified. If `frequency` is omitted,
      the resulting timestamps (a Pandas `DatetimeIndex` object)
      will have `periods` linearly spaced elements between `start_time` and
      `end_time` (closed on both sides). Learn more about frequency strings at
      [Offset aliases](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases).

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

    # -------------------------------------------------------------- Important
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    # ------------------------------------------------------------------------

    if csv:
        from fastapi.responses import StreamingResponse

        streaming_data = [
            (str(timestamp), photovoltaic_power)
            for timestamp, photovoltaic_power in zip(
                timestamps.tolist(), photovoltaic_power_output_series.series.tolist()  # type: ignore
            )
        ]

        if not csv.endswith(".csv"):
            filename = f"{csv}.csv"
        else:
            filename = csv
        
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
    
    response:dict = {}
    headers = {
                "Content-Disposition": f'attachment; filename="{PHOTOVOLTAIC_POWER_OUTPUT_FILENAME}.json"'
            }
    
    if fingerprint:
        response[FINGERPRINT_COLUMN_NAME] = photovoltaic_power_output_series.components[
            FINGERPRINT_COLUMN_NAME
        ]    
    
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


    if statistics:
        from pvgisprototype.api.series.statistics import calculate_series_statistics

        series_statistics = calculate_series_statistics(
            data_array=photovoltaic_power_output_series.series,
            timestamps=timestamps,
            groupby=groupby,  # type: ignore[arg-type]
        )
        response["Statistics"] = convert_numpy_arrays_to_lists(series_statistics)

    if not quiet:
        if verbose > 0:
            response = convert_numpy_arrays_to_lists(
                photovoltaic_power_output_series.components
            )
        else:
            response = {
                PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_output_series.series,
            }

    # finally
    return ORJSONResponse(response, headers=headers, media_type="application/json")

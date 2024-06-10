import numpy as np
from typing import Annotated
from typing import Optional
from typing import List
from fastapi import Query
from fastapi import Depends
import orjson
from fastapi.responses import Response
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.api.irradiance.models import PVModuleEfficiencyAlgorithm
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.constants import PHOTOVOLTAIC_MODULE_DEFAULT, ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT
from pvgisprototype.cli.typer.position import typer_option_zero_negative_solar_incidence_angle
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import ALBEDO_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import SYSTEM_EFFICIENCY_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LINKE_TURBIDITY_DEFAULT
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import FINGERPRINT_COLUMN_NAME
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.api.power.broadband import calculate_photovoltaic_power_output_series
from pvgisprototype.web_api.dependencies import fastapi_dependable_longitude
from pvgisprototype.web_api.dependencies import fastapi_dependable_latitude
from pvgisprototype.web_api.dependencies import fastapi_dependable_timestamps
from pvgisprototype.web_api.dependencies import fastapi_dependable_naive_timestamps
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_elevation
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_start_time
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_periods
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_frequency
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_end_time
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_timezone
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_random_time_series
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_mask_and_scale
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_neighbor_lookup
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_tolerance
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_in_memory 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_surface_tilt 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_surface_orientation 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_linke_turbidity_factor_series 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_apply_atmospheric_refraction 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_refracted_solar_zenith 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_albedo 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_apply_angular_loss_factor 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_solar_position_model 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_solar_incidence_model 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_solar_time_model 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_time_offset_global 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_hour_offset 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_solar_constant 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_perigee_offset 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_eccentricity_correction_factor 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_system_efficiency 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_power_model 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_efficiency 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_rounding_places 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_verbose 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_log 
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_module_temperature_algorithm
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_photovoltaic_module_model
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_fingerprint
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_surface_tilt_list
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_surface_orientation_list
from pvgisprototype.api.power.broadband_multiple_surfaces import calculate_photovoltaic_power_output_series_from_multiple_surfaces

from pvgisprototype.web_api.dependencies import fastapi_dependable_temperature_series
from pvgisprototype.web_api.dependencies import fastapi_dependable_wind_speed_series
from pvgisprototype.web_api.dependencies import fastapi_dependable_spectral_factor_series
from pvgisprototype import TemperatureSeries
from pvgisprototype import WindSpeedSeries
from pvgisprototype import SpectralFactorSeries


from pvgisprototype.web_api.fastapi_parameters import fastapi_query_global_horizontal_irradiance
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_direct_horizontal_irradiance
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_temperature_series
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_wind_speed_series
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_rounding_places
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_statistics
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_groupby
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_uniplot
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_uniplot_terminal_width
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_quiet
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_command_metadata
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_profiling

from pvgisprototype.constants import cPROFILE_FLAG_DEFAULT
from pvgisprototype.constants import TEMPERATURE_DEFAULT
from pvgisprototype.constants import SPECTRAL_FACTOR_DEFAULT
from pvgisprototype.constants import WIND_SPEED_DEFAULT
from pvgisprototype.constants import EFFICIENCY_DEFAULT
from pvgisprototype.constants import MULTI_THREAD_FLAG_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import STATISTICS_FLAG_DEFAULT
from pvgisprototype.constants import GROUPBY_DEFAULT
from pvgisprototype.constants import UNIPLOT_FLAG_DEFAULT
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.constants import INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT
from pvgisprototype.constants import QUIET_FLAG_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import FINGERPRINT_FLAG_DEFAULT
from pvgisprototype.constants import METADATA_FLAG_DEFAULT
from pvgisprototype.constants import POWER_UNIT
from pandas import DatetimeIndex

from pvgisprototype.web_api.fastapi_parameters import fastapi_query_surface_tilt_list
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_surface_orientation_list
from pvgisprototype.web_api.dependencies import fastapi_dependable_temperature_series
from pvgisprototype.web_api.dependencies import fastapi_dependable_wind_speed_series
from pvgisprototype.web_api.dependencies import fastapi_dependable_spectral_factor_series
from pvgisprototype import TemperatureSeries
from pvgisprototype import WindSpeedSeries
from pvgisprototype import SpectralFactorSeries
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.constants import NEIGHBOR_LOOKUP_DEFAULT
from typing import Dict, Any


def convert_numpy_arrays_to_lists(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    """Convert all NumPy arrays in the input dictionary to lists.

    Parameters
    ----------
        dictionary (Dict[str, Any]):
            The input dictionary possibly containing NumPy arrays.

    Returns
    -------
        Dict[str, Any]: A new dictionary with all NumPy arrays converted to lists.

    """
    output_dict = {}
    for key, value in dictionary.items():
        if isinstance(value, np.datetime64):
            print(f'I am here!')
            from pandas import to_datetime
            output_dict[key] = to_datetime(str(value)).isoformat()
        elif isinstance(value, np.ndarray):
            output_dict[key] = value.tolist()  # Convert NumPy array to list
        elif isinstance(value, np.float64 | np.float32):
            output_dict[key] = float(value)
        else:
            output_dict[key] = value
    return output_dict


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
    plt.plot(months, monthly_means, marker='o', linestyle='-', color='b')
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
    elevation: Annotated[float, fastapi_query_elevation] = 214,
    surface_orientation: Annotated[Optional[float], fastapi_query_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[Optional[float], fastapi_query_surface_tilt] = SURFACE_TILT_DEFAULT,
    timestamps: Annotated[DatetimeIndex, fastapi_dependable_timestamps] = None, 
    start_time: Annotated[datetime, fastapi_query_start_time] = None,
    #frequency: Annotated[str, fastapi_query_frequency] = 'h',
    end_time: Annotated[datetime, fastapi_query_end_time] = None,
    timezone: Annotated[Optional[str], fastapi_query_timezone] = ZoneInfo('UTC'),
    #random_time_series: Annotated[Optional[bool], fastapi_query_random_time_series] = False,
    global_horizontal_irradiance: Annotated[Optional[Path], fastapi_query_global_horizontal_irradiance] = None,
    direct_horizontal_irradiance: Annotated[Optional[Path], fastapi_query_direct_horizontal_irradiance] = None,
    # temperature_series: Annotated[float, fastapi_query_temperature_series] = TEMPERATURE_DEFAULT,
    temperature_series: Optional[TemperatureSeries] = fastapi_dependable_temperature_series,
    # wind_speed_series: Annotated[float, fastapi_query_wind_speed_series] = WIND_SPEED_DEFAULT,
    wind_speed_series: Optional[WindSpeedSeries] = fastapi_dependable_wind_speed_series,
    spectral_factor_series: Optional[SpectralFactorSeries] = fastapi_dependable_spectral_factor_series,
    # spectral_factor_series: Optional[Path] = Query(SPECTRAL_FACTOR_DEFAULT),
    neighbor_lookup: Annotated[MethodForInexactMatches, fastapi_query_neighbor_lookup] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[Optional[float], fastapi_query_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[Optional[bool], fastapi_query_mask_and_scale] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, fastapi_query_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    linke_turbidity_factor_series: Annotated[float, fastapi_query_linke_turbidity_factor_series] = LINKE_TURBIDITY_DEFAULT,
    apply_atmospheric_refraction: Annotated[Optional[bool], fastapi_query_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[float, fastapi_query_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: Annotated[Optional[float], fastapi_query_albedo] = ALBEDO_DEFAULT,
    apply_angular_loss_factor: Annotated[Optional[bool], fastapi_query_apply_angular_loss_factor] = True,
    solar_position_model: Annotated[SolarPositionModel, fastapi_query_solar_position_model] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[SolarIncidenceModel, fastapi_query_solar_incidence_model] = SolarIncidenceModel.jenco,
    zero_negative_solar_incidence_angle: Annotated[bool, typer_option_zero_negative_solar_incidence_angle] = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: Annotated[SolarTimeModel, fastapi_query_solar_time_model] = SOLAR_TIME_ALGORITHM_DEFAULT,
    time_offset_global: Annotated[float, fastapi_query_time_offset_global] = 0,
    hour_offset: Annotated[float, fastapi_query_hour_offset] = 0,
    solar_constant: Annotated[float, fastapi_query_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, fastapi_query_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, fastapi_query_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    photovoltaic_module: Annotated[PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model] = PHOTOVOLTAIC_MODULE_DEFAULT, #PhotovoltaicModuleModel.CSI_FREE_STANDING, 
    system_efficiency: Annotated[Optional[float], fastapi_query_system_efficiency] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[Optional[PVModuleEfficiencyAlgorithm], fastapi_query_power_model] = PVModuleEfficiencyAlgorithm.king,
    temperature_model: Annotated[ModuleTemperatureAlgorithm, fastapi_query_module_temperature_algorithm] = ModuleTemperatureAlgorithm.faiman,
    efficiency: Annotated[Optional[float], fastapi_query_efficiency] = EFFICIENCY_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = MULTI_THREAD_FLAG_DEFAULT,
    rounding_places: Annotated[Optional[int], fastapi_query_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, fastapi_query_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[Optional[str], fastapi_query_groupby] = GROUPBY_DEFAULT,
    csv: bool = False,
    # uniplot: Annotated[bool, fastapi_query_uniplot] = UNIPLOT_FLAG_DEFAULT,
    # terminal_width_fraction: Annotated[float, fastapi_query_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
    quiet: Annotated[bool, fastapi_query_quiet] = QUIET_FLAG_DEFAULT,
    log: Annotated[int, fastapi_query_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, fastapi_query_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    metadata: Annotated[bool, fastapi_query_command_metadata] = METADATA_FLAG_DEFAULT,
    profile: Annotated[bool, fastapi_query_profiling] = cPROFILE_FLAG_DEFAULT,
):
    """Estimate the photovoltaic power output for a solar surface.

    Estimate the photovoltaic power for a solar surface over a time series or
    an arbitrarily aggregated energy production of a PV system connected to the
    electricity grid (without battery storage) based on broadband solar
    irradiance, ambient temperature and wind speed.

    """
    surface_tilt = np.radians(surface_tilt)
    surface_orientation = np.radians(surface_orientation)
        
    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        #global_horizontal_irradiance=global_horizontal_irradiance,
        #direct_horizontal_irradiance=direct_horizontal_irradiance,
        spectral_factor_series=spectral_factor_series,
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
        dtype=dtype,
        array_backend=array_backend,
        multi_thread=multi_thread,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        linke_turbidity_factor_series=LinkeTurbidityFactor(value=linke_turbidity_factor_series),
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        albedo=albedo,
        apply_angular_loss_factor=apply_angular_loss_factor,
        solar_position_model=solar_position_model,
        solar_incidence_model=solar_incidence_model,
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        photovoltaic_module=photovoltaic_module,
        system_efficiency=system_efficiency,
        power_model=power_model,
        temperature_model=temperature_model,
        efficiency=efficiency,
        verbose=verbose,
        log=log,
        fingerprint=True,
        profile=profile,
    )
    if csv:
        from fastapi.responses import StreamingResponse
        from datetime import datetime
        streaming_data = [(str(timestamp), photovoltaic_power) for timestamp, photovoltaic_power in zip(timestamps.tolist(), photovoltaic_power_output_series.value.tolist())]
        filename = f"photovoltaic_power_output_{photovoltaic_power_output_series.components[FINGERPRINT_COLUMN_NAME]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        csv_content = ','.join(['Timestamp', 'Photovoltaic Power']) + '\n'
        csv_content += '\n'.join([','.join([timestamp, str(photovoltaic_power)]) for timestamp, photovoltaic_power in streaming_data]) + '\n'
        response_csv = StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers = {"Content-Disposition": f"attachment; filename={filename}"}
            )
        return response_csv

    if not quiet:
        response = {}
        
        if verbose > 0:
            response = convert_numpy_arrays_to_lists(photovoltaic_power_output_series.components)

        else:
            if fingerprint:
                response["fingerprint"] = photovoltaic_power_output_series.components[FINGERPRINT_COLUMN_NAME]
            response = {
                "Photovoltaic power output series": photovoltaic_power_output_series.value.tolist(),
                }

        print(f'{response=}')
        headers = {'Content-Disposition': 'attachment; filename="pvgis_photovoltaic_power_series.json"'}
        return Response(orjson.dumps(response), headers=headers, media_type="application/json")


async def get_photovoltaic_power_series(
    longitude: Annotated[float, fastapi_dependable_longitude] = 8.628,
    latitude: Annotated[float, fastapi_dependable_latitude] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214,
    surface_orientation: Annotated[Optional[float], fastapi_query_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[Optional[float], fastapi_query_surface_tilt] = SURFACE_TILT_DEFAULT,
    timestamps: Annotated[DatetimeIndex, fastapi_dependable_naive_timestamps] = None, 
    start_time: Annotated[datetime, fastapi_query_start_time] = None,
    periods: Annotated[int, fastapi_query_periods] = None,
    frequency: Annotated[str, fastapi_query_frequency] = 'h',
    end_time: Annotated[datetime, fastapi_query_end_time] = None,
    timezone: Annotated[Optional[str], fastapi_query_timezone] = ZoneInfo('UTC'),
    # temperature_series: Annotated[float, fastapi_query_temperature_series] = TEMPERATURE_DEFAULT,
    temperature_series: Optional[TemperatureSeries] = fastapi_dependable_temperature_series,
    # wind_speed_series: Annotated[float, fastapi_query_wind_speed_series] = WIND_SPEED_DEFAULT,
    wind_speed_series: Optional[WindSpeedSeries] = fastapi_dependable_wind_speed_series,
    spectral_factor_series: Optional[SpectralFactorSeries] = fastapi_dependable_spectral_factor_series,
    # spectral_factor_series: Optional[Path] = Query(SPECTRAL_FACTOR_DEFAULT),
    # neighbor_lookup: Annotated[MethodForInexactMatches, fastapi_query_neighbor_lookup] = NEIGHBOR_LOOKUP_DEFAULT,
    # tolerance: Annotated[Optional[float], fastapi_query_tolerance] = TOLERANCE_DEFAULT,
    # mask_and_scale: Annotated[Optional[bool], fastapi_query_mask_and_scale] = MASK_AND_SCALE_FLAG_DEFAULT,
    # linke_turbidity_factor_series: Annotated[float, fastapi_query_linke_turbidity_factor_series] = LINKE_TURBIDITY_DEFAULT,
    # apply_atmospheric_refraction: Annotated[Optional[bool], fastapi_query_apply_atmospheric_refraction] = True,
    # albedo: Annotated[Optional[float], fastapi_query_albedo] = ALBEDO_DEFAULT,
    # apply_angular_loss_factor: Annotated[Optional[bool], fastapi_query_apply_angular_loss_factor] = True,
    # solar_position_model: Annotated[SolarPositionModel, fastapi_query_solar_position_model] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    # solar_incidence_model: Annotated[SolarIncidenceModel, fastapi_query_solar_incidence_model] = SolarIncidenceModel.jenco,
    # solar_time_model: Annotated[SolarTimeModel, fastapi_query_solar_time_model] = SOLAR_TIME_ALGORITHM_DEFAULT,
    photovoltaic_module: Annotated[PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model] = PHOTOVOLTAIC_MODULE_DEFAULT, #PhotovoltaicModuleModel.CSI_FREE_STANDING, 
    system_efficiency: Annotated[Optional[float], fastapi_query_system_efficiency] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[Optional[PVModuleEfficiencyAlgorithm], fastapi_query_power_model] = PVModuleEfficiencyAlgorithm.king,
    # temperature_model: Annotated[ModuleTemperatureAlgorithm, fastapi_query_module_temperature_algorithm] = ModuleTemperatureAlgorithm.faiman,
    # efficiency: Annotated[Optional[float], fastapi_query_efficiency] = EFFICIENCY_DEFAULT,
    # rounding_places: Annotated[Optional[int], fastapi_query_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, fastapi_query_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[Optional[str], fastapi_query_groupby] = GROUPBY_DEFAULT,
    csv: bool = False,
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
    quiet: Annotated[bool, fastapi_query_quiet] = QUIET_FLAG_DEFAULT,
    # log: Annotated[int, fastapi_query_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, fastapi_query_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    # metadata: Annotated[bool, fastapi_query_command_metadata] = METADATA_FLAG_DEFAULT,
    # profile: Annotated[bool, fastapi_query_profiling] = cPROFILE_FLAG_DEFAULT,
):
    surface_tilt = np.radians(surface_tilt)
    surface_orientation = np.radians(surface_orientation)
        
    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        global_horizontal_irradiance=Path("sarah2_sis_over_esti_jrc.nc"),
        direct_horizontal_irradiance=Path("sarah2_sid_over_esti_jrc.nc"),
        spectral_factor_series=spectral_factor_series,
        temperature_series=Path("era5_t2m_over_esti_jrc.nc"),
        wind_speed_series=Path("era5_ws2m_over_esti_jrc.nc"),
        # temperature_series=temperature_series,
        # wind_speed_series=wind_speed_series,
        # mask_and_scale=mask_and_scale,
        # neighbor_lookup=neighbor_lookup,
        # tolerance=tolerance,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        # linke_turbidity_factor_series=LinkeTurbidityFactor(value=linke_turbidity_factor_series),
        # apply_atmospheric_refraction=apply_atmospheric_refraction,
        # albedo=albedo,
        # apply_angular_loss_factor=apply_angular_loss_factor,
        # solar_position_model=solar_position_model,
        # solar_incidence_model=solar_incidence_model,
        # solar_time_model=solar_time_model,
        photovoltaic_module=photovoltaic_module,
        system_efficiency=system_efficiency,
        power_model=power_model,
        # temperature_model=temperature_model,
        # efficiency=efficiency,
        verbose=verbose,
        # log=log,
        fingerprint=fingerprint,
        # profile=profile,
    )
    if csv:
        from fastapi.responses import StreamingResponse
        from datetime import datetime
        streaming_data = [(str(timestamp), photovoltaic_power) for timestamp, photovoltaic_power in zip(timestamps.tolist(), photovoltaic_power_output_series.value.tolist())]
        filename = f"photovoltaic_power_output_{photovoltaic_power_output_series.components[FINGERPRINT_COLUMN_NAME]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        csv_content = ','.join(['Timestamp', 'Photovoltaic Power']) + '\n'
        csv_content += '\n'.join([','.join([timestamp, str(photovoltaic_power)]) for timestamp, photovoltaic_power in streaming_data]) + '\n'
        response_csv = StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers = {"Content-Disposition": f"attachment; filename={filename}"}
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
                "Photovoltaic power output series": photovoltaic_power_output_series.value.tolist(),
            }

        # print(f'{response=}')
        # headers = {'Content-Disposition': 'attachment; filename="pvgis_photovoltaic_power_series.json"'}
        # return Response(orjson.dumps(response), headers=headers, media_type="application/json")
    if fingerprint:
        response["fingerprint"] = photovoltaic_power_output_series.components[
            FINGERPRINT_COLUMN_NAME
        ]

    if statistics:
        from pvgisprototype.api.series.statistics import calculate_series_statistics

        series_statistics = calculate_series_statistics(
            data_array=photovoltaic_power_output_series.value,
            timestamps=timestamps,
            groupby=groupby,
        )
        response["statistics"] = convert_numpy_arrays_to_lists(series_statistics)

    # finally
    headers = {
        "Content-Disposition": 'attachment; filename="pvgis_photovoltaic_power_series.json"'
    }
    return Response(
        orjson.dumps(response), headers=headers, media_type="application/json"
    )


async def get_photovoltaic_power_series_monthly_average(
    longitude: Annotated[float, fastapi_dependable_longitude] = 8.628,
    latitude: Annotated[float, fastapi_dependable_latitude] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214,
    surface_orientation: Annotated[Optional[float], fastapi_query_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[Optional[float], fastapi_query_surface_tilt] = SURFACE_TILT_DEFAULT,
    timestamps: Annotated[DatetimeIndex, fastapi_dependable_naive_timestamps] = None, 
    start_time: Annotated[datetime, fastapi_query_start_time] = '2005-01-01',
    end_time: Annotated[datetime, fastapi_query_end_time] = '2020-12-31',
    timezone: Annotated[Optional[str], fastapi_query_timezone] = ZoneInfo('UTC'),
    # temperature_series: Annotated[float, fastapi_query_temperature_series] = TEMPERATURE_DEFAULT,
    # temperature_series: Optional[TemperatureSeries] = fastapi_dependable_temperature_series,
    # wind_speed_series: Annotated[float, fastapi_query_wind_speed_series] = WIND_SPEED_DEFAULT,
    # wind_speed_series: Optional[WindSpeedSeries] = fastapi_dependable_wind_speed_series,
    spectral_factor_series: Optional[SpectralFactorSeries] = fastapi_dependable_spectral_factor_series,
    # spectral_factor_series: Optional[Path] = Query(SPECTRAL_FACTOR_DEFAULT),
    # neighbor_lookup: Annotated[MethodForInexactMatches, fastapi_query_neighbor_lookup] = NEIGHBOR_LOOKUP_DEFAULT,
    # tolerance: Annotated[Optional[float], fastapi_query_tolerance] = TOLERANCE_DEFAULT,
    # mask_and_scale: Annotated[Optional[bool], fastapi_query_mask_and_scale] = MASK_AND_SCALE_FLAG_DEFAULT,
    # linke_turbidity_factor_series: Annotated[float, fastapi_query_linke_turbidity_factor_series] = LINKE_TURBIDITY_DEFAULT,
    # apply_atmospheric_refraction: Annotated[Optional[bool], fastapi_query_apply_atmospheric_refraction] = True,
    # albedo: Annotated[Optional[float], fastapi_query_albedo] = ALBEDO_DEFAULT,
    # apply_angular_loss_factor: Annotated[Optional[bool], fastapi_query_apply_angular_loss_factor] = True,
    # solar_position_model: Annotated[SolarPositionModel, fastapi_query_solar_position_model] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    # solar_incidence_model: Annotated[SolarIncidenceModel, fastapi_query_solar_incidence_model] = SolarIncidenceModel.jenco,
    # solar_time_model: Annotated[SolarTimeModel, fastapi_query_solar_time_model] = SOLAR_TIME_ALGORITHM_DEFAULT,
    photovoltaic_module: Annotated[PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model] = PHOTOVOLTAIC_MODULE_DEFAULT, #PhotovoltaicModuleModel.CSI_FREE_STANDING, 
    system_efficiency: Annotated[Optional[float], fastapi_query_system_efficiency] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[Optional[PVModuleEfficiencyAlgorithm], fastapi_query_power_model] = PVModuleEfficiencyAlgorithm.king,
    # temperature_model: Annotated[ModuleTemperatureAlgorithm, fastapi_query_module_temperature_algorithm] = ModuleTemperatureAlgorithm.faiman,
    # efficiency: Annotated[Optional[float], fastapi_query_efficiency] = EFFICIENCY_DEFAULT,
    # rounding_places: Annotated[Optional[int], fastapi_query_rounding_places] = ROUNDING_PLACES_DEFAULT,
    # statistics: Annotated[bool, fastapi_query_statistics] = STATISTICS_FLAG_DEFAULT,
    # groupby: Annotated[Optional[str], fastapi_query_groupby] = GROUPBY_DEFAULT,
    csv: bool = False,
    plot_statistics: bool = False,
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
    # quiet: Annotated[bool, fastapi_query_quiet] = QUIET_FLAG_DEFAULT,
    # log: Annotated[int, fastapi_query_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, fastapi_query_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    # metadata: Annotated[bool, fastapi_query_command_metadata] = METADATA_FLAG_DEFAULT,
    # profile: Annotated[bool, fastapi_query_profiling] = cPROFILE_FLAG_DEFAULT,
):
    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        surface_tilt = np.radians(surface_tilt),
        surface_orientation = np.radians(surface_orientation),
        timestamps=timestamps,
        timezone=timezone,
        global_horizontal_irradiance=Path("sarah2_sis_over_esti_jrc.nc"),
        direct_horizontal_irradiance=Path("sarah2_sid_over_esti_jrc.nc"),
        temperature_series=Path("era5_t2m_over_esti_jrc.nc"),
        wind_speed_series=Path("era5_ws2m_over_esti_jrc.nc"),
        spectral_factor_series=spectral_factor_series,
        # mask_and_scale=mask_and_scale,
        # neighbor_lookup=neighbor_lookup,
        # tolerance=tolerance,
        # linke_turbidity_factor_series=LinkeTurbidityFactor(value=linke_turbidity_factor_series),
        # apply_atmospheric_refraction=apply_atmospheric_refraction,
        # albedo=albedo,
        # apply_angular_loss_factor=apply_angular_loss_factor,
        # solar_position_model=solar_position_model,
        # solar_incidence_model=solar_incidence_model,
        # solar_time_model=solar_time_model,
        photovoltaic_module=photovoltaic_module,
        system_efficiency=system_efficiency,
        power_model=power_model,
        efficiency=EFFICIENCY_DEFAULT,
        verbose=verbose,
        fingerprint=fingerprint,
    )
    if csv:
        from fastapi.responses import StreamingResponse
        from datetime import datetime

        streaming_data = [
            (str(timestamp), photovoltaic_power)
            for timestamp, photovoltaic_power in zip(
                timestamps.tolist(), photovoltaic_power_output_series.value.tolist()
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
            print(f'{series_statistics=}')
            plot_file = plot_monthly_means(series_statistics, "monthly_means_plot")

            from fastapi.responses import FileResponse
            return FileResponse(path=plot_file, filename=Path(plot_file).name, media_type='image/png')

    headers = {
        "Content-Disposition": 'attachment; filename="pvgis_photovoltaic_power_series.json"'
    }
    return Response(
        orjson.dumps(response), headers=headers, media_type="application/json"
    )


async def get_photovoltaic_power_output_series_multi(
    longitude: Annotated[float, fastapi_dependable_longitude] = 8.628,
    latitude: Annotated[float, fastapi_dependable_latitude] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214,
    surface_orientation: Annotated[list[float], fastapi_query_surface_orientation_list] = [float(SURFACE_ORIENTATION_DEFAULT)],
    surface_tilt: Annotated[list[float], fastapi_query_surface_tilt_list] = [float(SURFACE_TILT_DEFAULT)],
    timestamps: Annotated[DatetimeIndex, fastapi_dependable_naive_timestamps] = None, 
    start_time: Annotated[datetime, fastapi_query_start_time] = None,
    periods: Annotated[int, fastapi_query_periods] = None,
    frequency: Annotated[str, fastapi_query_frequency] = 'h',
    end_time: Annotated[datetime, fastapi_query_end_time] = None,
    timezone: Annotated[Optional[str], fastapi_query_timezone] = ZoneInfo('UTC'),
    #random_time_series: Annotated[Optional[bool], fastapi_query_random_time_series] = False,
    #global_horizontal_irradiance: Optional[Path] = Query(None),
    #direct_horizontal_irradiance: Optional[Path] = Query(None),
    spectral_factor_series: Optional[SpectralFactorSeries] = fastapi_dependable_spectral_factor_series,
    temperature_series: Optional[TemperatureSeries] = fastapi_dependable_temperature_series,
    wind_speed_series: Optional[WindSpeedSeries] = fastapi_dependable_wind_speed_series,
    # global_horizontal_irradiance: Annotated[Optional[Path], fastapi_query_global_horizontal_irradiance] = None,
    # direct_horizontal_irradiance: Annotated[Optional[Path], fastapi_query_direct_horizontal_irradiance] = None,
    neighbor_lookup: Annotated[MethodForInexactMatches, fastapi_query_neighbor_lookup] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[Optional[float], fastapi_query_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[Optional[bool], fastapi_query_mask_and_scale] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, fastapi_query_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = MULTI_THREAD_FLAG_DEFAULT,
    linke_turbidity_factor_series: Annotated[float, fastapi_query_linke_turbidity_factor_series] = LINKE_TURBIDITY_DEFAULT,
    apply_atmospheric_refraction: Annotated[Optional[bool], fastapi_query_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[float, fastapi_query_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: Annotated[Optional[float], fastapi_query_albedo] = ALBEDO_DEFAULT,
    apply_angular_loss_factor: Annotated[Optional[bool], fastapi_query_apply_angular_loss_factor] = True,
    solar_position_model: Annotated[SolarPositionModel, fastapi_query_solar_position_model] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[SolarIncidenceModel, fastapi_query_solar_incidence_model] = SolarIncidenceModel.jenco,
    solar_time_model: Annotated[SolarTimeModel, fastapi_query_solar_time_model] = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: Annotated[float, fastapi_query_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, fastapi_query_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, fastapi_query_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    photovoltaic_module: Annotated[PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model] = PHOTOVOLTAIC_MODULE_DEFAULT, #PhotovoltaicModuleModel.CSI_FREE_STANDING, 
    system_efficiency: Annotated[Optional[float], fastapi_query_system_efficiency] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[Optional[PVModuleEfficiencyAlgorithm], fastapi_query_power_model] = PVModuleEfficiencyAlgorithm.king,
    temperature_model: Annotated[ModuleTemperatureAlgorithm, fastapi_query_module_temperature_algorithm] = ModuleTemperatureAlgorithm.faiman,
    efficiency: Annotated[Optional[float], fastapi_query_efficiency] = EFFICIENCY_DEFAULT,
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[int, fastapi_query_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, fastapi_query_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    profile: Annotated[bool, fastapi_query_profiling] = cPROFILE_FLAG_DEFAULT,
    csv: bool = False,
):
    if len(surface_orientation) != len(surface_tilt):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Surface tilt options and surface orientation options must have the same number of inputs")

    surface_tilt_radians = []
    for surface_tilt_value in surface_tilt:
        surface_tilt_radians.append(np.radians(surface_tilt_value))
    surface_orientation_radians = []
    for surface_orientation_value in surface_orientation:
        surface_orientation_radians.append(np.radians(surface_orientation_value))

    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series_from_multiple_surfaces(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        spectral_factor_series=spectral_factor_series,
        # temperature_series=temperature_series,
        # wind_speed_series=wind_speed_series,
        temperature_series=Path("era5_t2m_over_esti_jrc.nc"),
        wind_speed_series=Path("era5_ws2m_over_esti_jrc.nc"),
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
        dtype=dtype,
        array_backend=array_backend,
        multi_thread=multi_thread,
        surface_orientation=surface_orientation_radians,
        surface_tilt=surface_tilt_radians,
        linke_turbidity_factor_series=LinkeTurbidityFactor(value=linke_turbidity_factor_series),
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        albedo=albedo,
        apply_angular_loss_factor=apply_angular_loss_factor,
        solar_position_model=solar_position_model,
        solar_incidence_model=solar_incidence_model,
        solar_time_model=solar_time_model,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        photovoltaic_module=photovoltaic_module,
        system_efficiency=system_efficiency,
        power_model=power_model,
        temperature_model=temperature_model,
        efficiency=efficiency,
        verbose=verbose,
        log=log,
        fingerprint=True,
        profile=profile,
    )

    response = {
        "Photovoltaic power output series": photovoltaic_power_output_series.series.tolist(),
        }

    if fingerprint:
        response["fingerprint"] = photovoltaic_power_output_series.components[FINGERPRINT_COLUMN_NAME]

    if csv:
        from fastapi.responses import StreamingResponse
        from datetime import datetime
        streaming_data = [(str(timestamp), photovoltaic_power) for timestamp, photovoltaic_power in zip(timestamps.tolist(), photovoltaic_power_output_series.value.tolist())]
        filename = f"photovoltaic_power_output_{photovoltaic_power_output_series.components[FINGERPRINT_COLUMN_NAME]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        csv_content = ','.join(['Timestamp', 'Photovoltaic Power']) + '\n'
        csv_content += '\n'.join([','.join([timestamp, str(photovoltaic_power)]) for timestamp, photovoltaic_power in streaming_data]) + '\n'

        response_csv = StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers = {"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        return response_csv

    headers = {'Content-Disposition': 'attachment; filename="data.json"'}
    return Response(orjson.dumps(response), headers=headers, media_type="application/json")

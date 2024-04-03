import numpy as np
from typing import Annotated
from typing import Optional
from typing import List
from fastapi import Query
from fastapi import Depends
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
from pvgisprototype.api.irradiance.models import MethodsForInexactMatches
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.constants import PHOTOVOLTAIC_MODULE_DEFAULT
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
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.api.power.broadband import calculate_photovoltaic_power_output_series
from pvgisprototype.web_api.dependencies import fastapi_dependable_longitude
from pvgisprototype.web_api.dependencies import fastapi_dependable_latitude
from pvgisprototype.web_api.dependencies import fastapi_dependable_timestamps
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_elevation
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_start_time
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
from pvgisprototype.api.utilities.timestamp import ctx_convert_to_timezone


async def get_photovoltaic_power_output_series(
    longitude: Annotated[float, fastapi_dependable_longitude],
    latitude: Annotated[float, fastapi_dependable_latitude],
    elevation: Annotated[float, fastapi_query_elevation],
    timestamps: Annotated[str, fastapi_dependable_timestamps] = None, 
    start_time: Annotated[datetime, fastapi_query_start_time] = None,
    frequency: Annotated[str, fastapi_query_frequency] = 'h',
    end_time: Annotated[datetime, fastapi_query_end_time] = None,
    # timezone: Annotated[Optional[str], Depends(ctx_convert_to_timezone)] = 'UTC',
    timezone: Annotated[Optional[str], fastapi_query_timezone] = ZoneInfo('UTC'),
    random_time_series: Annotated[Optional[bool], fastapi_query_random_time_series] = False,
    global_horizontal_irradiance: Optional[Path] = Query(None),
    direct_horizontal_irradiance: Optional[Path] = Query(None),
    spectral_factor_series: Optional[Path] = Query(None),
    temperature_series: Optional[Path] = Query(25),
    wind_speed_series: Optional[Path] = Query(0),
    # global_horizontal_irradiance: Annotated[Optional[Path], fastapi_query_global_horizontal_irradiance] = None,
    # direct_horizontal_irradiance: Annotated[Optional[Path], fastapi_query_direct_horizontal_irradiance] = None,
    # temperature_series: Annotated[float, fastapi_query_temperature_series] = 25,
    # wind_speed_series: Annotated[float, fastapi_query_wind_speed_series] = 0,
    mask_and_scale: Annotated[Optional[bool], fastapi_query_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodsForInexactMatches, fastapi_query_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], fastapi_query_tolerance] = TOLERANCE_DEFAULT,
    in_memory: Annotated[bool, fastapi_query_in_memory] = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = True,
    surface_orientation: Annotated[Optional[float], fastapi_query_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[Optional[float], fastapi_query_surface_tilt] = SURFACE_TILT_DEFAULT,
    linke_turbidity_factor_series: Annotated[float, fastapi_query_linke_turbidity_factor_series] = LINKE_TURBIDITY_DEFAULT,
    apply_atmospheric_refraction: Annotated[Optional[bool], fastapi_query_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[float, fastapi_query_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: Annotated[Optional[float], fastapi_query_albedo] = ALBEDO_DEFAULT,
    apply_angular_loss_factor: Annotated[Optional[bool], fastapi_query_apply_angular_loss_factor] = True,
    solar_position_model: Annotated[SolarPositionModel, fastapi_query_solar_position_model] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[SolarIncidenceModel, fastapi_query_solar_incidence_model] = SolarIncidenceModel.jenco,
    solar_time_model: Annotated[SolarTimeModel, fastapi_query_solar_time_model] = SOLAR_TIME_ALGORITHM_DEFAULT,
    time_offset_global: Annotated[float, fastapi_query_time_offset_global] = 0,
    hour_offset: Annotated[float, fastapi_query_hour_offset] = 0,
    solar_constant: Annotated[float, fastapi_query_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, fastapi_query_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, fastapi_query_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    # time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    # angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    # angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    # horizon_heights: Annotated[List[float], typer.Argument(help="Array of horizon elevations.")] = None,
    photovoltaic_module: Annotated[PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model] = PHOTOVOLTAIC_MODULE_DEFAULT, #PhotovoltaicModuleModel.CSI_FREE_STANDING, 
    system_efficiency: Annotated[Optional[float], fastapi_query_system_efficiency] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[Optional[PVModuleEfficiencyAlgorithm], fastapi_query_power_model] = None,
    temperature_model: Annotated[ModuleTemperatureAlgorithm, fastapi_query_module_temperature_algorithm] = ModuleTemperatureAlgorithm.faiman,
    efficiency: Annotated[Optional[float], fastapi_query_efficiency] = None,
    # rounding_places: Annotated[Optional[int], fastapi_query_rounding_places] = 5,
    # statistics: Annotated[bool, typer_option_statistics] = False,
    # groupby: Annotated[Optional[str], typer_option_groupby] = None,
    # csv: Annotated[Path, typer_option_csv] = None,
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[int, fastapi_query_log] = 0,
    # index: Annotated[bool, typer_option_index] = False,
    fingerprint: Annotated[bool, fastapi_query_fingerprint] = False,
    profile: bool = False, 
):
    surface_tilt = np.radians(surface_tilt)
    surface_orientation = np.radians(surface_orientation)

    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        # periods=periods,
        frequency=frequency,
        timezone=timezone,
        random_time_series=random_time_series,
        global_horizontal_irradiance=global_horizontal_irradiance,
        direct_horizontal_irradiance=direct_horizontal_irradiance,
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
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        # time_output_units=time_output_units,
        # angle_units=angle_units,
        # angle_output_units=angle_output_units,
        # horizon_heights=horizon_heights,
        photovoltaic_module=photovoltaic_module,
        system_efficiency=system_efficiency,
        power_model=power_model,
        temperature_model=temperature_model,
        efficiency=efficiency,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
        profile=profile,
    )  # Re-Design Me ! ------------------------------------------------
    from devtools import debug
    debug(locals())

    return {"Photovoltaic power output series": photovoltaic_power_output_series.value.tolist()}

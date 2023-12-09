import numpy as np
from typing import Optional
from typing import List
from fastapi import Query
from fastapi import Depends
from datetime import datetime
from pathlib import Path
from pvgisprototype.api.geometry.models import SolarPositionModel
from pvgisprototype.api.geometry.models import SolarTimeModel
from pvgisprototype.api.geometry.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SolarIncidenceModel
from pvgisprototype.api.irradiance.models import PVModuleEfficiencyAlgorithm
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
from pvgisprototype.api.irradiance.models import MethodsForInexactMatches
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import SYSTEM_EFFICIENCY_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LINKE_TURBIDITY_DEFAULT
from pvgisprototype.constants import RADIANS
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.web_api.dependencies import process_series_timestamp
from pvgisprototype.api.irradiance.power import calculate_photovoltaic_power_output_series
from pvgisprototype.api.utilities.conversions import convert_to_radians_fastapi
from pvgisprototype.web_api.dependencies import process_longitude
from pvgisprototype.web_api.dependencies import process_latitude


TRYITOUT_LONGITUDE = 8.622676
TRYITOUT_LATITUDE = 45.
TRYITOUT_TIMESTAMP = '2020-02-02 20:00:02'


async def get_photovoltaic_power_output_series(
    longitude: float = Depends(process_longitude),
    latitude: float = Depends(process_latitude),
    elevation: float = Query(...),
    timestamps: Optional[List[datetime]] = Depends(process_series_timestamp),
    start_time: Optional[datetime] = Query(None),
    frequency: Optional[str] = Query('H'),
    end_time: Optional[datetime] = Query(None),
    timezone: Optional[str] = Query(None),
    random_time_series: bool = Query(False),
    global_horizontal_component: Optional[Path] = Query(None),
    direct_horizontal_component: Optional[Path] = Query(None),
    temperature_series: float = Query(25),
    wind_speed_series: float = Query(0),
    mask_and_scale: bool = Query(False),
    neighbor_lookup: MethodsForInexactMatches = Query(None),
    tolerance: Optional[float] = Query(TOLERANCE_DEFAULT),
    in_memory: bool = Query(False),
    surface_tilt: Optional[float] = Query(SURFACE_TILT_DEFAULT),
    surface_orientation: Optional[float] = Query(SURFACE_ORIENTATION_DEFAULT),
    linke_turbidity_factor_series: float = Query(LINKE_TURBIDITY_DEFAULT),
    apply_atmospheric_refraction: Optional[bool] =  Query(True),
    refracted_solar_zenith: float = Query(REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT),
    albedo: Optional[float] = Query(2),
    apply_angular_loss_factor: Optional[bool] = Query(True),
    solar_position_model: SolarPositionModel = Query(SOLAR_POSITION_ALGORITHM_DEFAULT),
    solar_incidence_model: SolarIncidenceModel = Query(SolarIncidenceModel.jenco),
    solar_time_model: SolarTimeModel = Query(SOLAR_TIME_ALGORITHM_DEFAULT),
    time_offset_global: float = Query(0),
    hour_offset: float = Query(0),
    solar_constant: float = Query(SOLAR_CONSTANT),
    perigee_offset: float = Query(PERIGEE_OFFSET),
    eccentricity_correction_factor: float = Query(ECCENTRICITY_CORRECTION_FACTOR),
    system_efficiency: Optional[float] = Query(SYSTEM_EFFICIENCY_DEFAULT),
    power_model: PVModuleEfficiencyAlgorithm = Query(None),
    efficiency: Optional[float] = Query(None),
    rounding_places: Optional[int] = Query(5),
    verbose: int = Query(VERBOSE_LEVEL_DEFAULT),
):
    surface_tilt = np.radians(surface_tilt)
    surface_orientation = np.radians(surface_orientation)
    photovoltaic_power_output_series, results, title = calculate_photovoltaic_power_output_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        frequency=frequency,
        timezone=timezone,
        random_time_series=random_time_series,
        global_horizontal_component=global_horizontal_component,
        direct_horizontal_component=direct_horizontal_component,
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
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
        system_efficiency=system_efficiency,
        power_model=power_model,
        efficiency=efficiency,
        verbose=verbose,
    )

    return photovoltaic_power_output_series.tolist()

from datetime import datetime
from fastapi import Depends, Query
from pvgisprototype.api.utilities.conversions import convert_to_radians_fastapi
from pvgisprototype.api.utilities.timestamp import convert_to_timezone
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.algorithms.noaa.solar_position import calculate_noaa_solar_position
from pvgisprototype.algorithms.noaa.solar_position import calculate_noaa_timeseries_solar_position
from typing import Optional
from typing import List
from pvgisprototype.constants import RADIANS
from pvgisprototype.web_api.dependencies import process_timestamp_input


async def get_calculate_noaa_solar_position(
    longitude: float = Query(..., ge=-180, le=180),
    latitude: float = Query(..., ge=-90, le=90),
    timestamp: Optional[datetime] = Query(None),
    timezone: Optional[str] = Query(None),
    refracted_solar_zenith: float = Query(1.5853349194640094),
    apply_atmospheric_refraction: Optional[bool] = Query(True),
    time_output_units: str = Query('minutes'),
    angle_units: str = Query(RADIANS),
    angle_output_units: str = Query(RADIANS),
    rounding_places: Optional[int] = Query(5),
    verbose: bool = Query(False)
):
    longitude = convert_to_radians_fastapi(longitude)
    latitude = convert_to_radians_fastapi(latitude)

    if timestamp is None:
        timestamp = now_utc_datetimezone()

    if timezone:
        timezone = convert_to_timezone(timezone)
        timestamp = timestamp.astimezone(timezone)


    solar_position_calculations = calculate_noaa_solar_position(
        longitude,
        latitude,
        timestamp,
        timezone,
        refracted_solar_zenith,
        apply_atmospheric_refraction,
        time_output_units,
        angle_units,
        angle_output_units,
    )

    return {"solar_position_table": solar_position_calculations}


async def get_calculate_noaa_timeseries_solar_position(
    longitude: float = Query(..., ge=-180, le=180),
    latitude: float = Query(..., ge=-90, le=90),
    timestamps: Optional[List[datetime]] = Depends(process_timestamp_input),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    timezone: Optional[str] = Query(None),
    refracted_solar_zenith: float = Query(1.5853349194640094),
    apply_atmospheric_refraction: Optional[bool] = Query(True),
    time_output_units: str = Query('minutes'),
    angle_output_units: str = Query(RADIANS),
    rounding_places: Optional[int] = Query(5),
    verbose: bool = Query(False)
):
    longitude = convert_to_radians_fastapi(longitude)
    latitude = convert_to_radians_fastapi(latitude)

    if timezone:
        timezone = convert_to_timezone(timezone)
        timestamps = [ts.astimezone(timezone) for ts in timestamps]

    solar_position_calculations = calculate_noaa_timeseries_solar_position(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )

    for quantity_name, quantity_object in solar_position_calculations.items():
        if not isinstance(quantity_object, list):
            try:
                angle_value = getattr(quantity_object, angle_output_units)
                angle_value_list = angle_value.tolist()
                solar_position_calculations[quantity_name] = [round(value, rounding_places) for value in angle_value_list]
            except AttributeError:
                time_value =  getattr(quantity_object, time_output_units)
                time_value_list = time_value.tolist()
                solar_position_calculations[quantity_name] = [round(value, rounding_places) for value in time_value_list]

    return {"solar_position_table": solar_position_calculations}
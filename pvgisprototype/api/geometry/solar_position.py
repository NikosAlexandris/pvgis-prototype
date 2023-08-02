from devtools import debug
import typer
from typing import Annotated
from typing import Optional
from typing import List
from typing import Tuple
from typing import NamedTuple
from enum import Enum
import numpy as np
import datetime
import suncalc
import pysolar
from ..utilities.conversions import convert_to_degrees_if_requested
from ..utilities.conversions import convert_to_radians_if_requested
from ..utilities.conversions import convert_to_radians
from ..utilities.timestamp import now_utc_datetimezone
from ..utilities.timestamp import ctx_convert_to_timezone
from ..utilities.timestamp import attach_timezone
from .time_models import SolarTimeModels
from .solar_altitude import calculate_solar_altitude
from .solar_azimuth import calculate_solar_azimuth
from .solar_declination import calculate_solar_declination
from ...models.skyfield.solar_geometry import calculate_solar_position_skyfield
from ...models.skyfield.solar_geometry import calculate_solar_altitude_azimuth_skyfield
from ...models.pvgis.solar_geometry import calculate_solar_position_pvgis
# from ...models.pvgis.solar_geometry import calculate_solar_time_pvgis
from ...models.pvgis.solar_geometry import calculate_solar_geometry_pvgis_constants
from ...models.noaa.solar_position import calculate_solar_altitude_noaa
from ...models.noaa.solar_position import calculate_solar_azimuth_noaa

from .solar_models import SolarPositionModels
from pvgisprototype.api.input_models import Latitude
from pvgisprototype.api.input_models import Longitude
from pvgisprototype.api.input_models import SolarPositionInput
from pvgisprototype.api.decorators import validate_with_pydantic


def _parse_model(
        ctx: typer.Context,
        model: List[SolarPositionModels],
        param: typer.CallbackParam,
    ) -> List[SolarPositionModels]:

    print(f'ctx : {ctx}')
    print(f'param : {param}')
    print(f'model : {model}')
    print()
    if ctx.resilient_parsing:
        return
    if SolarPositionModels.all in model:
        # Return all models except for the 'all' itself!
        model = [model for model in SolarPositionModels if model != SolarPositionModels.all]
    print(f"Return model: {model}")
    return model


@validate_with_pydantic(SolarPositionInput, expand_args=True)
def model_solar_position(
        longitude: Longitude,
        latitude: Latitude,
        timestamp: datetime,
        timezone: str = None,
        model: SolarPositionModels = SolarPositionModels.skyfield,
        apply_atmospheric_refraction: bool = True,
        time_output_units: str = 'minutes',
        angle_output_units: str = 'radians',
    )-> Tuple[NamedTuple, NamedTuple]:
    """
    The solar altitude angle measures from the horizon up towards the zenith
    (positive, and down towards the nadir (negative)). The altitude is zero all
    along the great circle between zenith and nadir.

    The solar azimuth angle measures horizontally around the horizon from north
    through east, south, and west.

    Notes
    -----

    - All solar calculation functions return floating angular measurements in
      radians.


    pysolar :

    From https://pysolar.readthedocs.io:

    - Altitude is reckoned with zero at the horizon. The altitude is positive
      when the sun is above the horizon.

    - Azimuth is reckoned with zero corresponding to north. Positive azimuth
      estimates correspond to estimates east of north; negative estimates, or
      estimates larger than 180 are west of north. In the northern hemisphere,
      if we speak in terms of (altitude, azimuth), the sun comes up around
      (0, 90), reaches (70, 180) around noon, and sets around (0, 270).

    - The result is returned with units.
    """
    if model.value == SolarPositionModels.noaa:

        solar_altitude = calculate_solar_altitude_noaa(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                time_output_units=time_output_units,
                angle_output_units=angle_output_units,
                )
        solar_altitude = convert_to_degrees_if_requested(
            solar_altitude,
            angle_output_units,
            )

        solar_azimuth = calculate_solar_azimuth_noaa(
            longitude,
            latitude,
            timestamp,
            timezone,
            apply_atmospheric_refraction,
            time_output_units,
            angle_output_units,
                )
        solar_azimuth = convert_to_degrees_if_requested(
            solar_azimuth,
            angle_output_units,
            )
    
    if model.value == SolarPositionModels.skyfield:
        solar_altitude, solar_azimuth = calculate_solar_altitude_azimuth_skyfield(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
    #             angle_output_units=angle_output_units,
    #             )
    #     solar_azimuth = convert_to_degrees_if_requested(
    #         solar_azimuth,
    #         angle_output_units,
    #         )
    #     solar_altitude = convert_to_degrees_if_requested(
    #         solar_altitude,
    #         angle_output_units,
    #         )
    
    # if model.value == SolarPositionModels.suncalc:
    #     # note : first azimuth, then altitude
    #     solar_azimuth, solar_altitude = suncalc.get_position(            # FIXME: Must return two named tuples (maybe wrap this func?)
    #             date=timestamp,  # this comes first here!
    #             lng=longitude,
    #             lat=latitude,
    #             ).values()
    #     solar_azimuth = convert_to_degrees_if_requested(
    #         solar_azimuth,
    #         angle_output_units,
    #         )
    #     solar_altitude = convert_to_degrees_if_requested(
    #         solar_altitude,
    #         angle_output_units,
    #         )
    
    # if model.value  == SolarPositionModels.pysolar:

    #     timestamp = attach_timezone(timestamp, timezone)
    #     solar_altitude = pysolar.solar.get_altitude(                    # FIXME: Must return a named tuple (maybe wrap this func?)
    #             latitude_deg=latitude,  # this comes first
    #             longitude_deg=longitude,
    #             when=timestamp,
    #             )  # returns degrees by default
    #     solar_altitude = convert_to_radians_if_requested(
    #         solar_altitude,
    #         angle_output_units,
    #         )

    #     solar_azimuth = pysolar.solar.get_azimuth(
    #             latitude_deg=longitude,  # this comes first        # FIXME: Must return a named tuple (maybe wrap this func?)
    #             longitude_deg=latitude,
    #             when=timestamp,
    #             )  # returns degrees by default
    #     solar_azimuth = convert_to_radians_if_requested(
    #         solar_azimuth,
    #         angle_output_units,
    #         )

    # if model.value  == SolarPositionModels.pvis:

    #     solar_altitude = calculate_solar_altitude(
    #             longitude=longitude,
    #             latitude=latitude,
    #             timestamp=timestamp,
    #             timezone=timezone,
    #             angle_output_units=angle_output_units,
    #             )
    #     solar_azimuth = calculate_solar_azimuth(
    #             longitude=longitude,
    #             latitude=latitude,
    #             timestamp=timestamp,
    #             angle_output_units=angle_output_units,
    #             )
                days_in_a_year=days_in_a_year,
                perigee_offset=perigee_offset,
                eccentricity=eccentricity,
                time_offset_global=time_offset_global,
                hour_offset=hour_offset,
                solar_time_model=solar_time_model,
                angle_output_units=angle_output_units,
                )
        solar_altitude = convert_to_degrees_if_requested(solar_altitude, angle_output_units)
        solar_azimuth = calculate_solar_azimuth(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            days_in_a_year=days_in_a_year,
            perigee_offset=perigee_offset,
            eccentricity=eccentricity,
            time_offset_global=time_offset_global,
            hour_offset=hour_offset,
            solar_time_model=solar_time_model,
            angle_output_units=angle_output_units,
        )
        solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, angle_output_units)

    # if model.value  == SolarPositionModels.pvgis:
        
    #     solar_declination = calculate_solar_declination(timestamp)
    #     local_solar_time, _units = calculate_solar_time_pvgis(
    #             longitude=longitude,
    #             latitude=latitude,
    #             timestamp=timestamp,
    #             )

    #     solar_geometry_pvgis_day_constants = calculate_solar_geometry_pvgis_constants(
    #             longitude=longitude,
    #             latitude=latitude,
    #             local_solar_time=local_solar_time,
    #             solar_declination=solar_declination.value,
    #             )

    #     solar_altitude, solar_azimuth, sun_azimuth = calculate_solar_position_pvgis(
    #             solar_geometry_pvgis_day_constants,
    #             timestamp,
    #             )

    #     solar_altitude = convert_to_radians_if_requested(solar_altitude, angle_output_units)
    #     solar_azimuth = convert_to_radians_if_requested(solar_azimuth, angle_output_units)

    debug(locals())
    return solar_altitude, solar_azimuth


def calculate_solar_position(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: str = None,
    models: List[SolarPositionModels] = [SolarPositionModels.skyfield],
    apply_atmospheric_refraction: bool = True,
    time_output_units: str = 'minutes',
    angle_output_units: str = 'radians',
) -> List:
    """
    Calculates the solar position using all models and returns the results in a table.
    """
    results = []
    for model in models:
        if model != SolarPositionModels.all:  # ignore 'all' in the enumeration
            solar_altitude, solar_azimuth = model_solar_position(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                model=model,
                solar_time_model=solar_time_model,
                days_in_a_year=days_in_a_year,
                perigee_offset=perigee_offset,
                eccentricity=eccentricity,
                time_offset_global=time_offset_global,
                hour_offset=hour_offset,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                time_output_units=time_output_units,
                angle_units=angle_units,
                angle_output_units=angle_output_units,
            )
            results.append({
                'Model': model.value,
                'Altitude': solar_altitude.value,
                'Azimuth': solar_azimuth.value,
                'Units': solar_altitude.unit,  # Don't trust me -- Redesign Me!
            })

    return results

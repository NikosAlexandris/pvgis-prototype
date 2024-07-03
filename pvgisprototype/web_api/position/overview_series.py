from datetime import datetime
from pathlib import Path
from typing import List, Optional
from zoneinfo import ZoneInfo

from fastapi import Depends, Query

from pvgisprototype.api.position.models import (
    SolarTimeModel,
)
from pvgisprototype.api.position.overview import (
    calculate_solar_geometry_overview_time_series,
)
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.constants import (
    ECCENTRICITY_CORRECTION_FACTOR,
    PERIGEE_OFFSET,
    RADIANS,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.web_api.dependencies import (
    process_latitude,
    process_longitude,
    process_series_timestamp,
)


async def overview_series(
    longitude: float = Depends(process_longitude),
    latitude: float = Depends(process_latitude),
    timestamps: Optional[List[datetime]] = Depends(process_series_timestamp),
    start_time: Optional[str] = Query(None),
    frequency: Optional[str] = Query("H"),
    end_time: Optional[str] = Query(None),
    timezone: Optional[str] = Query(None),
    random_time_series: bool = Query(False),
    model: List[SolarTimeModel] = Query(
        [SolarTimeModel.skyfield], description="Model to calculate solar time"
    ),
    apply_atmospheric_refraction: Optional[bool] = Query(True),
    solar_time_model: SolarTimeModel = Query(SolarTimeModel.milne),
    perigee_offset: float = Query(PERIGEE_OFFSET),
    eccentricity_correction_factor: float = Query(ECCENTRICITY_CORRECTION_FACTOR),
    angle_output_units: str = Query(RADIANS),
    rounding_places: Optional[int] = Query(5),
    group_models: Optional[bool] = Query(
        False, description="Visually cluster time series results per model"
    ),
    statistics: bool = Query(False, description="Generate statistics"),
    csv: Path = Query(None, description="Generate a CSV"),
    verbose: int = Query(VERBOSE_LEVEL_DEFAULT),
    index: bool = Query(False, description="Show index column"),
):
    """ """
    # print(f'Context: {ctx}')
    # print(f'Context: {ctx.params}')
    # print(f"Invoked subcommand: {ctx.invoked_subcommand}")

    # if ctx.invoked_subcommand is not None:
    #     print("Skipping default command to run sub-command.")
    #     return

    # elif ctx.invoked_subcommand in ['altitude', 'azimuth']:
    #     print('Execute subcommand')

    # else:
    #     print('Yay')
    #     return

    # Initialize with None ---------------------------------------------------
    user_requested_timestamps = None
    user_requested_timezone = None
    # -------------------------------------------- Smarter way to do this? ---

    utc_zoneinfo = ZoneInfo("UTC")
    if timestamps.tzinfo != utc_zoneinfo:
        # Note the input timestamp and timezone
        user_requested_timestamps = timestamps
        user_requested_timezone = timezone

        # timestamps = timestamps.tz_convert(utc_zoneinfo)

        timezone = utc_zoneinfo
        print(
            f"Input timestamps & zone ({user_requested_timestamps} & {user_requested_timezone}) converted to {timestamps} for all internal calculations!"
        )

    solar_position_series = calculate_solar_geometry_overview_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_models=model,  # could be named models!
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        # refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    from pvgisprototype.cli.print import print_solar_position_series_table

    print_solar_position_series_table(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        table=solar_position_series,
        timing=True,
        declination=True,
        hour_angle=True,
        zenith=True,
        altitude=True,
        azimuth=True,
        incidence=True,
        user_requested_timestamps=user_requested_timestamps,
        user_requested_timezone=user_requested_timezone,
        rounding_places=rounding_places,
        group_models=group_models,
    )

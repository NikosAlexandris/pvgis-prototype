from zoneinfo import ZoneInfo
from devtools import debug
from pvgisprototype.core.arrays import create_array
import numpy as np
import pandas as pd
from pvgisprototype.api.position.models import SolarEvent, SolarPositionModel, SolarPositionParameter, SolarTimeModel
from pvgisprototype import EventTime, Latitude, Longitude, UnrefractedSolarZenith
from pandas import DatetimeIndex

from pvgisprototype.algorithms.noaa.event_time import calculate_solar_event_time_series_noaa
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HOUR_ANGLE_NAME,
    LOG_LEVEL_DEFAULT,
    NOT_AVAILABLE,
    POSITION_ALGORITHM_NAME,
    RADIANS,
    SOLAR_EVENTS_NAME,
    SOLAR_EVENT_COLUMN_NAME,
    SOLAR_EVENT_TIME_COLUMN_NAME,
    TIME_ALGORITHM_NAME,
    TIMEZONE_UTC,
    UNIT_NAME,
    UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from typing import List


def model_solar_event_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo = ZoneInfo(TIMEZONE_UTC),
    event: List[SolarEvent | None] = [None],
    unrefracted_solar_zenith: UnrefractedSolarZenith = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    # adjust_for_atmospheric_refraction: bool = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
    """
    """
    event_time_series = calculate_solar_event_time_series_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,#.normalize().unique(),
            event=event,
            unrefracted_solar_zenith=unrefracted_solar_zenith,
            timezone=timezone,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
    )

    return event_time_series


def calculate_event_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo = ZoneInfo(TIMEZONE_UTC),
    event: List[SolarEvent | None] = [None],
    unrefracted_solar_zenith: UnrefractedSolarZenith = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    # adjust_for_atmospheric_refraction: bool = False,
    # adjust_for_atmospheric_refraction: bool = False,
    solar_position_models: List[SolarPositionModel] = [SolarPositionModel.noaa],
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
    """
    """
    # empty_array = create_array(
    #     timestamps.shape, dtype="object", init_method="empty", backend=array_backend
    # )
    results = {}
    for solar_position_model in solar_position_models:
        # for the time being! ------------------------------------------------
        if solar_position_model != SolarPositionModel.noaa:
            logger.warning(
                f"Solar geometry overview series is not implemented for the requested solar position model: {solar_position_model}!"
            )
        # --------------------------------------------------------------------
        if (
            solar_position_model != SolarPositionModel.all
        ):  # ignore 'all' in the enumeration
            solar_event_series = model_solar_event_time_series(
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    event=event,
                    unrefracted_solar_zenith=unrefracted_solar_zenith,
                    timezone=timezone,
                    dtype=dtype,
                    array_backend=array_backend,
                    verbose=verbose,
                    log=log,
            )
            solar_position_model_overview = {
                solar_position_model.name: {
                    POSITION_ALGORITHM_NAME: solar_position_model.value,
                    # TIME_ALGORITHM_NAME: (
                    #     solar_hour_angle_series.timing_algorithm
                    #     if solar_hour_angle_series
                    #     else NOT_AVAILABLE
                    # ),
                    # HOUR_ANGLE_NAME: (
                    #     getattr(
                    #         solar_hour_angle_series, angle_output_units, NOT_AVAILABLE
                    #     )
                    #     if solar_hour_angle_series
                    #     else NOT_AVAILABLE
                    # ),
                    SOLAR_EVENTS_NAME: (  # Requested solar events
                        event
                        if event
                        else NOT_AVAILABLE
                    ),
                    **(
                        {SolarPositionParameter.event_type: solar_event_series.event}
                        if solar_event_series.event is not None and not (
                            isinstance(solar_event_series.event, (list, np.ndarray)) and
                            all(x is None for x in solar_event_series.event)
                        )
                        else {}
                    ),
                    **(
                        {SolarPositionParameter.event_time: solar_event_series.value}
                        if solar_event_series.value is not None and not (
                            isinstance(solar_event_series.value, pd.DatetimeIndex) and
                            all(pd.isna(x) for x in solar_event_series.value)
                        )
                        else {}
                    ),
                }
            }
            results = results | solar_position_model_overview

    print(f'results : {results}')
    return results

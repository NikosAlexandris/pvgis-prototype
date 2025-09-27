import asyncio
from os import environ
from pathlib import Path
from typing import Annotated, Optional
from fastapi import Depends, HTTPException, Request
from pandas import DatetimeIndex
from xarray import DataArray

from pvgisprototype.api.series.direct_horizontal_irradiance import (
    get_direct_horizontal_irradiance_series,
)
from pvgisprototype.api.series.global_horizontal_irradiance import (
    get_global_horizontal_irradiance_series,
)
from pvgisprototype.api.series.spectral_factor import get_spectral_factor_series
from pvgisprototype.api.series.temperature import get_temperature_series
from pvgisprototype.api.series.wind_speed import get_wind_speed_series
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEGREES,
    IN_MEMORY_FLAG_DEFAULT,
    LOG_LEVEL_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    MULTI_THREAD_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import logger
from pvgisprototype.web_api.dependency.location import (
    process_longitude,
    process_latitude,
)
from pvgisprototype.web_api.dependency.time import (
    process_start_time,
    process_end_time,
    process_frequency,
    process_timezone,
    process_timezone_to_be_converted,
)
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_direct_horizontal_irradiance,
    fastapi_query_global_horizontal_irradiance,
    fastapi_query_horizon_profile_series,
    fastapi_query_spectral_effect_series,
    fastapi_query_temperature_series,
    fastapi_query_verbose,
    fastapi_query_wind_speed_series,
    fastapi_query_time_offset,
    fastapi_query_time_offset_variable,
    fastapi_query_horizon_profile,
    fastapi_query_verbose,
    fastapi_query_horizon_profile,
    fastapi_query_verbose,
)
from pvgisprototype.web_api.config import get_settings
from pvgisprototype.web_api.config.options import DataReadMode
from pvgisprototype.web_api.schemas import (
    Frequency,
    Timezone,
)
from pvgisprototype.api.datetime.datetimeindex import generate_timestamps
from pvgisprototype.log import logger
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_convert_timestamps,
    fastapi_query_periods,
    fastapi_query_timestamps,
    fastapi_query_use_timestamps_from_data,
    fastapi_query_convert_timestamps,
    fastapi_query_periods,
    fastapi_query_timestamps,
    fastapi_query_use_timestamps_from_data,
)
from pvgisprototype.web_api.schemas import (
    Frequency,
    Timezone,
)
from fastapi import Depends
from typing import Annotated, Optional
from xarray import DataArray

from pvgisprototype.api.datetime.datetimeindex import generate_timestamps
from pvgisprototype.log import logger
from pvgisprototype.web_api.schemas import (
    Frequency,
    Timezone,
)
from fastapi import Depends
from xarray import DataArray

from pvgisprototype.constants import (
    DEGREES,
)
from typing import Annotated

from fastapi import Depends, HTTPException
from numpy import radians
from xarray import DataArray

from pvgisprototype.cli.typer.shading import infer_horizon_azimuth_in_radians
from pvgisprototype.constants import (
    DEGREES,
    VERBOSE_LEVEL_DEFAULT,
)
from typing import Annotated
from fastapi import Depends, HTTPException
from numpy import radians
from xarray import DataArray
from pvgisprototype.cli.typer.shading import infer_horizon_azimuth_in_radians
from pvgisprototype.constants import (
    DEGREES,
    VERBOSE_LEVEL_DEFAULT,
)


async def _provide_common_datasets(
    global_horizontal_irradiance: Annotated[
        str, fastapi_query_global_horizontal_irradiance
    ] = "sarah2_sis_over_esti_jrc.nc",
    direct_horizontal_irradiance: Annotated[
        str, fastapi_query_direct_horizontal_irradiance
    ] = "sarah2_sid_over_esti_jrc.nc",
    temperature_series: Annotated[
        str, fastapi_query_temperature_series
    ] = "era5_t2m_over_esti_jrc.nc",
    wind_speed_series: Annotated[
        str, fastapi_query_wind_speed_series
    ] = "era5_ws2m_over_esti_jrc.nc",
    spectral_factor_series: Annotated[
        str, fastapi_query_spectral_effect_series
    ] = "spectral_effect_cSi_over_esti_jrc.nc",
    horizon_profile_series: Annotated[
        str, fastapi_query_horizon_profile_series
    ] = "horizon_profile_over_esti_jrc.zarr",
    time_offset: Annotated[str | None, fastapi_query_time_offset] = None,
):
    """This is a helper function for providing the SIS, SID, temperature, wind speed, spectral effect data.
    This method is a deprecated temporary solution and will be replaced in the future.
    """

    # Load data paths from environment variables with defaults
    global_horizontal_irradiance = environ.get(
        "PVGIS_WEB_API_GLOBAL_HORIZONTAL_IRRADIANCE_PATH", global_horizontal_irradiance
    )
    direct_horizontal_irradiance = environ.get(
        "PVGIS_WEB_API_DIRECT_HORIZONTAL_IRRADIANCE_PATH", direct_horizontal_irradiance
    )
    temperature_series = environ.get(
        "PVGIS_WEB_API_TEMPERATURE_PATH", temperature_series
    )
    wind_speed_series = environ.get("PVGIS_WEB_API_WIND_SPEED_PATH", wind_speed_series)
    spectral_factor_series = environ.get(
        "PVGIS_WEB_API_SPECTRAL_FACTOR_PATH", spectral_factor_series
    )
    horizon_profile_series = environ.get(
        "PVGIS_WEB_API_HORIZON_PROFILE_PATH", horizon_profile_series
    )
    time_offset = environ.get("PVGIS_WEB_API_TIME_OFFSET_PATH", time_offset)

    return {
        "global_horizontal_irradiance_series": Path(
            global_horizontal_irradiance
        ).resolve(strict=True),
        "direct_horizontal_irradiance_series": Path(
            direct_horizontal_irradiance
        ).resolve(strict=True),
        "temperature_series": Path(temperature_series).resolve(strict=True),
        "wind_speed_series": Path(wind_speed_series).resolve(strict=True),
        "spectral_factor_series": Path(spectral_factor_series).resolve(strict=True),
        "horizon_profile_series": Path(horizon_profile_series).resolve(strict=True),
        "time_offset": Path(time_offset).resolve(strict=True) if time_offset else None,
    }




async def process_horizon_profile(
    common_datasets: Annotated[dict, Depends(_provide_common_datasets)],
    horizon_profile: Annotated[str | None, fastapi_query_horizon_profile] = "None",
    longitude: Annotated[float, Depends(process_longitude)] = 8.628,
    latitude: Annotated[float, Depends(process_latitude)] = 45.812,
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    if horizon_profile == "PVGIS":
        from pvgisprototype.api.series.utilities import select_location_time_series
        from pvgisprototype.api.utilities.conversions import (
            convert_float_to_degrees_if_requested,
        )

        horizon_profile = select_location_time_series(
            time_series=common_datasets["horizon_profile_series"],
            variable=None,
            coordinate=None,
            minimum=None,
            maximum=None,
            longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
            latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
            verbose=verbose,
        )

        return horizon_profile

    elif (
        horizon_profile == "None"
    ):  # NOTE WHY THIS IS HAPPENING? FASTAPI DOES NOT UNDERSTAND NONE VALUE!!!
        return None
    else:
        from numpy import fromstring

        try:
            horizon_profile_array = fromstring(
                horizon_profile, sep=","  # type: ignore[arg-type]
            )  # NOTE Parse user input
            _horizon_azimuth_radians = infer_horizon_azimuth_in_radians(
                horizon_profile_array
            )  # NOTE Process it
            horizon_profile = DataArray(  # type: ignore[assignment]
                radians(horizon_profile_array),
                coords={
                    "azimuth": _horizon_azimuth_radians,
                },
                dims=["azimuth"],
                name="horizon_height",
            )

            return horizon_profile

        except Exception as exception:
            raise HTTPException(
                status_code=400,
                detail=str(exception),
            )



async def process_horizon_profile_no_read(
    horizon_profile: Annotated[str | None, fastapi_query_horizon_profile] = "None",
):
    """Process horizon profile input. No read of a dataset is happening here,
    only preparation.
    - If `horizon_profile` is "PVGIS" then the function returns "PVGIS" and the reading
    of the data is going to happend in the `_read_datasets` asynchronous function
    - If `horizon_profile` is "None" then returns None and no data reading is going to
    happen in the `_read_datasets` asynchronous function
    - In any other case it is assumed that the user provided horizon heights so the `xarray.DataArray`
    is prepared and forward to the software. Again no data reading is going to happen in the
    `_read_datasets` asynchronous function

    Parameters
    ----------
    horizon_profile : Annotated[str  |  None, fastapi_query_horizon_profile], optional
        Horizon profile option, by default "PVGIS"
    """
    if horizon_profile == "PVGIS":
        return horizon_profile
    elif (
        horizon_profile == "None"
    ):  # NOTE WHY THIS IS HAPPENING? FASTAPI DOES NOT UNDERSTAND NONE VALUE!!!
        return None
    else:
        from numpy import fromstring

        try:
            horizon_profile_array = fromstring(
                horizon_profile, sep=","  # type: ignore[arg-type]
            )  # NOTE Parse user input
            _horizon_azimuth_radians = infer_horizon_azimuth_in_radians(
                horizon_profile_array
            )  # NOTE Process it
            horizon_profile = DataArray(  # type: ignore[assignment]
                radians(horizon_profile_array),
                coords={
                    "azimuth": _horizon_azimuth_radians,
                },
                dims=["azimuth"],
                name="horizon_height",
            )

            return horizon_profile

        except Exception:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse option horizon_profile={horizon_profile}!",
            )


async def _get_preopened_datasets(request: Request) -> dict | None:
    """Get preopened datasets from app state if available."""
    try:
        return getattr(request.app.state, "preopened_datasets", None)
    except AttributeError:
        return None


async def process_time_offset(
    preopened_datasets: Annotated[dict | None, Depends(_get_preopened_datasets)],
    variable: Annotated[str, fastapi_query_time_offset_variable] = None,
    longitude: Annotated[float, Depends(process_longitude)] = 8.628,
    latitude: Annotated[float, Depends(process_latitude)] = 45.812,
) -> DataArray | None:
    if preopened_datasets["time_offset"] is not None:
        from pvgisprototype.api.utilities.conversions import (
            convert_float_to_degrees_if_requested,
        )

        if variable is not None:
            offset = (
                preopened_datasets["time_offset"][variable]
                .sel(
                    lon=convert_float_to_degrees_if_requested(longitude, DEGREES),
                    lat=convert_float_to_degrees_if_requested(latitude, DEGREES),
                    method="nearest",
                )
                .values
            )
        else:
            offset = (
                preopened_datasets["time_offset"]
                .sel(
                    lon=convert_float_to_degrees_if_requested(longitude, DEGREES),
                    lat=convert_float_to_degrees_if_requested(latitude, DEGREES),
                    method="nearest",
                )
                .values
            )

        return offset

    return None


async def process_timestamps(
    common_datasets: Annotated[dict, Depends(_provide_common_datasets)],
    preopened_datasets: Annotated[dict | None, Depends(_get_preopened_datasets)],
    time_offset: Annotated[DataArray | None, Depends(process_time_offset)] = None,
    timestamps_from_data: Annotated[
        bool, fastapi_query_use_timestamps_from_data
    ] = True,  # NOTE USED ONLY INTERNALLY FOR RESPECTING OR NOT THE DATA TIMESTAMPS ##### NOTE NOTE NOTE Re-name read_timestamps_from_data
    timestamps: Annotated[str | None, fastapi_query_timestamps] = None,
    start_time: Annotated[str | None, Depends(process_start_time)] = "2013-01-01",
    periods: Annotated[int | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, Depends(process_frequency)] = Frequency.Hourly,
    end_time: Annotated[str | None, Depends(process_end_time)] = "2013-12-31",
    timezone: Annotated[Optional[Timezone], Depends(process_timezone)] = Timezone.UTC,  # type: ignore[attr-defined]
) -> DatetimeIndex:
    """ """
    if timestamps_from_data:
        if preopened_datasets:
            logger.debug("> Searching pre-opened datasets for generating timestamps...")

            dataset_keys = [
                "global_horizontal_irradiance_series",
                "direct_horizontal_irradiance_series",
                "spectral_factor_series",
            ]

            data_file = next(
                (
                    preopened_datasets[key]
                    for key in dataset_keys
                    if key in preopened_datasets
                ),
                None,
            )
            logger.debug(
                f"> Fetched pre-opened dataset for generating timestamps: {data_file}"
            )
        else:
            logger.debug(
                "> Falling back to reading datasets from files for generating timestamps..."
            )
            data_file = None
            if any(
                [
                    common_datasets["global_horizontal_irradiance_series"],
                    common_datasets["direct_horizontal_irradiance_series"],
                    common_datasets["spectral_factor_series"],
                ]
            ):
                data_file = next(
                    filter(
                        None,
                        [
                            common_datasets["global_horizontal_irradiance_series"],
                            common_datasets["direct_horizontal_irradiance_series"],
                            common_datasets["spectral_factor_series"],
                        ],
                    )
                )

    if start_time is not None or end_time is not None or periods is not None:
        try:
            timestamps = generate_timestamps(
                data_file=data_file,
                time_offset=time_offset,
                start_time=start_time,
                end_time=end_time,
                periods=periods,  # type: ignore
                frequency=frequency,
                timezone=timezone,  # type: ignore[arg-type]
                name=None,
            )
        except Exception as exception:
            raise HTTPException(
                status_code=400,
                detail=str(exception),
            )

    if timestamps.tzinfo:  # type: ignore
        timestamps = timestamps.tz_localize(None)  # type: ignore

    return timestamps


async def _read_datasets_from_paths(
    common_datasets: Annotated[dict, Depends(_provide_common_datasets)],
    longitude: Annotated[float, Depends(process_longitude)] = 8.628,
    latitude: Annotated[float, Depends(process_latitude)] = 45.812,
    timestamps: Annotated[str | None, Depends(process_timestamps)] = None,
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
    horizon_profile: Annotated[
        str | None, Depends(process_horizon_profile_no_read)
    ] = "PVGIS",
):
    other_kwargs = {
        "neighbor_lookup": NEIGHBOR_LOOKUP_DEFAULT,
        "tolerance": TOLERANCE_DEFAULT,
        "mask_and_scale": MASK_AND_SCALE_FLAG_DEFAULT,
        "in_memory": IN_MEMORY_FLAG_DEFAULT,
        "dtype": DATA_TYPE_DEFAULT,
        "array_backend": ARRAY_BACKEND_DEFAULT,
        "multi_thread": MULTI_THREAD_FLAG_DEFAULT,
    }

    async with asyncio.TaskGroup() as task_group:

        temperature_task = task_group.create_task(
            asyncio.to_thread(
                get_temperature_series,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                temperature_series=common_datasets["temperature_series"],
                verbose=verbose,
                **other_kwargs,  # type: ignore
            )
        )
        wind_speed_task = task_group.create_task(
            asyncio.to_thread(
                get_wind_speed_series,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                wind_speed_series=common_datasets["wind_speed_series"],
                verbose=verbose,
                **other_kwargs,  # type: ignore
            )
        )
        global_horizontal_irradiance_task = task_group.create_task(
            asyncio.to_thread(
                get_global_horizontal_irradiance_series,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                global_horizontal_irradiance_series=common_datasets[
                    "global_horizontal_irradiance_series"
                ],
                verbose=verbose,
                **other_kwargs,  # type: ignore
            )
        )
        direct_horizontal_irradiance_task = task_group.create_task(
            asyncio.to_thread(
                get_direct_horizontal_irradiance_series,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                direct_horizontal_irradiance_series=common_datasets[
                    "direct_horizontal_irradiance_series"
                ],
                verbose=verbose,
                **other_kwargs,  # type: ignore
            )
        )
        spectral_factor_task = task_group.create_task(
            asyncio.to_thread(
                get_spectral_factor_series,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                spectral_factor_series=common_datasets["spectral_factor_series"],
                verbose=verbose,
                **other_kwargs,  # type: ignore
            )
        )

        if not isinstance(horizon_profile, DataArray):
            if horizon_profile == "PVGIS":
                from pvgisprototype.api.series.utilities import (
                    select_location_time_series,
                )
                from pvgisprototype.api.utilities.conversions import (
                    convert_float_to_degrees_if_requested,
                )

                horizon_profile_task = task_group.create_task(
                    asyncio.to_thread(
                        select_location_time_series,
                        time_series=common_datasets["horizon_profile_series"],
                        variable=None,
                        coordinate=None,
                        minimum=None,
                        maximum=None,
                        longitude=convert_float_to_degrees_if_requested(
                            longitude, DEGREES
                        ),
                        latitude=convert_float_to_degrees_if_requested(
                            latitude, DEGREES
                        ),
                        verbose=verbose,
                    )
                )

    return {
        "global_horizontal_irradiance_series": global_horizontal_irradiance_task.result(),
        "direct_horizontal_irradiance_series": direct_horizontal_irradiance_task.result(),
        "temperature_series": temperature_task.result(),
        "wind_speed_series": wind_speed_task.result(),
        "spectral_factor_series": spectral_factor_task.result(),
        "horizon_profile": (
            horizon_profile
            if (isinstance(horizon_profile, DataArray) or (horizon_profile is None))
            else horizon_profile_task.result()
        ),
    }


async def _read_datasets(
    common_datasets: Annotated[dict, Depends(_provide_common_datasets)],
    preloaded_datasets: Annotated[dict | None, Depends(_get_preopened_datasets)],
    longitude: Annotated[float, Depends(process_longitude)] = 8.628,
    latitude: Annotated[float, Depends(process_latitude)] = 45.812,
    timestamps: Annotated[str | None, Depends(process_timestamps)] = None,
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
    horizon_profile: Annotated[
        str | None, Depends(process_horizon_profile_no_read)
    ] = "PVGIS",
):
    """Extract multiple meteorological time series datasets in parallel for a specific location.

    Efficiently extracts temperature, wind speed, irradiance, and spectral factor time series
    data for a given geographic location and time period. Uses pre-opened (lazy loaded) datasets when
    available for optimal performance, otherwise falls back to reading from files. All
    data extraction tasks are executed concurrently using asyncio.TaskGroup for maximum
    efficiency.

    Parameters
    ----------
    common_datasets : dict
        Dictionary mapping dataset names to file paths for fallback data loading.
        Injected via FastAPI dependency.
    preloaded_datasets : dict | None
        Dictionary of pre-opened (lazy loaded) xarray datasets from application state.
        When available, provides significant performance improvements. Injected via
        FastAPI dependency.
    longitude : float, optional
        Longitude coordinate for data extraction in degrees,
        by default 8.628
    latitude : float, optional
        Latitude coordinate for data extraction in degrees,
        by default 45.812
    timestamps : str | None, optional
        Time index for temporal selection of the data. Injected via FastAPI dependency,
        by default None
    verbose : int, optional
        Verbosity level for debug output during data extraction,
        by default VERBOSE_LEVEL_DEFAULT
    horizon_profile : str | None, optional
        Horizon profile data source. "PVGIS" uses built-in data, or can be a custom
        DataArray. Injected via FastAPI dependency, by default "PVGIS"

    Returns
    -------
    dict
        Dictionary containing extracted time series data with keys:
        - "global_horizontal_irradiance_series": GlobalHorizontalIrradianceSeries object
        - "direct_horizontal_irradiance_series": DirectHorizontalIrradianceSeries object
        - "temperature_series": TemperatureSeries object
        - "wind_speed_series": WindSpeedSeries object
        - "spectral_factor_series": SpectralFactorSeries object
        - "horizon_profile": DataArray or processed horizon profile data

    Notes
    -----
    This function is optimized for FastAPI web API usage with dependency injection.
    All time series extraction tasks run concurrently using asyncio.TaskGroup,
    significantly reducing total processing time compared to sequential execution.

    The function automatically chooses between pre-opened (lazy loaded) datasets (faster) and file
    reading (fallback) based on availability. Pre-opened datasets are preferred as
    they eliminate file I/O overhead during API requests.

    Standard extraction parameters (neighbor_lookup, tolerance, dtype, log level)
    are applied consistently across all datasets for uniform processing behavior.
    """
    from pvgisprototype.api.series.direct_horizontal_irradiance import (
        get_direct_horizontal_irradiance_series_from_array_or_set,
    )
    from pvgisprototype.api.series.global_horizontal_irradiance import (
        get_global_horizontal_irradiance_series_from_array_or_set,
    )
    from pvgisprototype.api.series.spectral_factor import (
        get_spectral_factor_series_from_array_or_set,
    )
    from pvgisprototype.api.series.temperature import (
        get_temperature_series_from_array_or_set,
    )
    from pvgisprototype.api.series.wind_speed import (
        get_wind_speed_series_from_array_or_set,
    )

    settings = get_settings()

    other_kwargs = {
        "neighbor_lookup": NEIGHBOR_LOOKUP_DEFAULT,
        "tolerance": TOLERANCE_DEFAULT,
        "dtype": DATA_TYPE_DEFAULT,
        "log": LOG_LEVEL_DEFAULT,
    }

    # Use preloaded datasets if available, otherwise fallback to file paths
    if preloaded_datasets:
        dataset_sources = preloaded_datasets
        logger.info("> Using pre-opened (lazy loaded) datasets from app state...")

    else:
        logger.error("> ⚠️ Could not find pre-opened datasets in app state.")
        raise HTTPException(
            status_code=500,
            detail="Internal server error - data initialization failed",
        )

    logger.info(f"> Data read mode: {settings.DATA_READ_MODE}")

    if settings.DATA_READ_MODE == DataReadMode.ASYNC:
        async with asyncio.TaskGroup() as task_group:

            temperature_task = task_group.create_task(
                asyncio.to_thread(
                    get_temperature_series_from_array_or_set,
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    temperature_series=dataset_sources["temperature_series"],
                    **other_kwargs,  # type: ignore
                )
            )
            wind_speed_task = task_group.create_task(
                asyncio.to_thread(
                    get_wind_speed_series_from_array_or_set,
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    wind_speed_series=dataset_sources["wind_speed_series"],
                    **other_kwargs,  # type: ignore
                )
            )
            global_horizontal_irradiance_task = task_group.create_task(
                asyncio.to_thread(
                    get_global_horizontal_irradiance_series_from_array_or_set,
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    global_horizontal_irradiance_series=dataset_sources[
                        "global_horizontal_irradiance_series"
                    ],
                    **other_kwargs,  # type: ignore
                )
            )
            direct_horizontal_irradiance_task = task_group.create_task(
                asyncio.to_thread(
                    get_direct_horizontal_irradiance_series_from_array_or_set,
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    direct_horizontal_irradiance_series=dataset_sources[
                        "direct_horizontal_irradiance_series"
                    ],
                    **other_kwargs,  # type: ignore
                )
            )
            spectral_factor_task = task_group.create_task(
                asyncio.to_thread(
                    get_spectral_factor_series_from_array_or_set,
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    spectral_factor_series=dataset_sources["spectral_factor_series"],
                    **other_kwargs,  # type: ignore
                )
            )

            if not isinstance(horizon_profile, DataArray):
                if horizon_profile == "PVGIS":
                    from pvgisprototype.api.series.utilities import (
                        select_location_time_series,
                    )
                    from pvgisprototype.api.utilities.conversions import (
                        convert_float_to_degrees_if_requested,
                    )

                    horizon_profile_task = task_group.create_task(
                        asyncio.to_thread(
                            select_location_time_series,
                            time_series=dataset_sources["horizon_profile_series"],
                            variable=None,
                            coordinate=None,
                            minimum=None,
                            maximum=None,
                            longitude=convert_float_to_degrees_if_requested(
                                longitude, DEGREES
                            ),
                            latitude=convert_float_to_degrees_if_requested(
                                latitude, DEGREES
                            ),
                            verbose=verbose,
                        )
                    )

        return {
            "global_horizontal_irradiance_series": global_horizontal_irradiance_task.result(),
            "direct_horizontal_irradiance_series": direct_horizontal_irradiance_task.result(),
            "temperature_series": temperature_task.result(),
            "wind_speed_series": wind_speed_task.result(),
            "spectral_factor_series": spectral_factor_task.result(),
            "horizon_profile": (
                horizon_profile
                if (isinstance(horizon_profile, DataArray) or (horizon_profile is None))
                else horizon_profile_task.result()
            ),
        }

    elif settings.DATA_READ_MODE == DataReadMode.SYNC:
        temperature_series = get_temperature_series_from_array_or_set(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            temperature_series=dataset_sources["temperature_series"],
            **other_kwargs,  # type: ignore
        )
        wind_speed_series = get_wind_speed_series_from_array_or_set(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            wind_speed_series=dataset_sources["wind_speed_series"],
            **other_kwargs,  # type: ignore
        )
        global_horizontal_irradiance_series = (
            get_global_horizontal_irradiance_series_from_array_or_set(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                global_horizontal_irradiance_series=dataset_sources[
                    "global_horizontal_irradiance_series"
                ],
                **other_kwargs,  # type: ignore
            )
        )
        direct_horizontal_irradiance_series = (
            get_direct_horizontal_irradiance_series_from_array_or_set(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                direct_horizontal_irradiance_series=dataset_sources[
                    "direct_horizontal_irradiance_series"
                ],
                **other_kwargs,  # type: ignore
            )
        )
        spectral_factor_series = get_spectral_factor_series_from_array_or_set(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            spectral_factor_series=dataset_sources["spectral_factor_series"],
            **other_kwargs,  # type: ignore
        )

        if not isinstance(horizon_profile, DataArray):
            if horizon_profile == "PVGIS":
                from pvgisprototype.api.series.utilities import (
                    select_location_time_series,
                )
                from pvgisprototype.api.utilities.conversions import (
                    convert_float_to_degrees_if_requested,
                )

                horizon_profile = select_location_time_series(
                    time_series=dataset_sources["horizon_profile_series"],
                    variable=None,
                    coordinate=None,
                    minimum=None,
                    maximum=None,
                    longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
                    latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
                    verbose=verbose,
                )

        return {
            "global_horizontal_irradiance_series": global_horizontal_irradiance_series,
            "direct_horizontal_irradiance_series": direct_horizontal_irradiance_series,
            "temperature_series": temperature_series,
            "wind_speed_series": wind_speed_series,
            "spectral_factor_series": spectral_factor_series,
            "horizon_profile": horizon_profile,
        }
    else:
        logger.error(f"> Invalid data read mode: {settings.DATA_READ_MODE}")
        raise HTTPException(
            status_code=500,
            detail="Internal server configuration error",
        )


async def process_timestamps_override_timestamps_from_data(
    common_datasets: Annotated[dict, Depends(_provide_common_datasets)],
    preopened_datasets: Annotated[dict | None, Depends(_get_preopened_datasets)],
    timestamps: Annotated[str | None, fastapi_query_timestamps] = None,
    start_time: Annotated[str | None, Depends(process_start_time)] = "2013-01-01",
    periods: Annotated[int | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, Depends(process_frequency)] = Frequency.Hourly,
    end_time: Annotated[str | None, Depends(process_end_time)] = "2013-12-31",
    timezone: Annotated[Optional[Timezone], Depends(process_timezone)] = Timezone.UTC,  # type: ignore[attr-defined]
) -> DatetimeIndex:
    return await process_timestamps(
        common_datasets=common_datasets,
        preopened_datasets=preopened_datasets,
        timestamps_from_data=False,  # NOTE Override the default here
        timestamps=timestamps,
        start_time=start_time,
        periods=periods,
        frequency=frequency,
        end_time=end_time,
        timezone=timezone,
    )


async def convert_timestamps_to_specified_timezone(
    timestamps: Annotated[str | None, Depends(process_timestamps)] = None,
    timezone: Annotated[Timezone, Depends(process_timezone)] = Timezone.UTC,  # type: ignore[attr-defined]
    user_requested_timestamps: Annotated[None, fastapi_query_convert_timestamps] = None,
    timezone_for_calculations: Annotated[
        Timezone, Depends(process_timezone_to_be_converted)
    ] = Timezone.UTC,  # type: ignore[attr-defined]
) -> DatetimeIndex:
    if timestamps.tz != timezone_for_calculations:  # type: ignore[union-attr]
        user_requested_timestamps = timestamps.tz_localize(timezone_for_calculations).tz_convert(timezone)  # type: ignore[union-attr]

    user_requested_timestamps = user_requested_timestamps.tz_localize(None)  # type: ignore[attr-defined]

    return user_requested_timestamps


async def convert_timestamps_to_specified_timezone_override_timestamps_from_data(
    timestamps: Annotated[
        str | None, Depends(process_timestamps_override_timestamps_from_data)
    ] = None,
    timezone: Annotated[Timezone, Depends(process_timezone)] = Timezone.UTC,  # type: ignore[attr-defined]
    user_requested_timestamps: Annotated[None, fastapi_query_convert_timestamps] = None,
    timezone_for_calculations: Annotated[
        Timezone, Depends(process_timezone_to_be_converted)
    ] = Timezone.UTC,  # type: ignore[attr-defined]
) -> DatetimeIndex:
    if timestamps.tz != timezone_for_calculations:  # type: ignore[union-attr]
        user_requested_timestamps = timestamps.tz_localize(timezone_for_calculations).tz_convert(timezone)  # type: ignore[union-attr]

    user_requested_timestamps = user_requested_timestamps.tz_localize(None)  # type: ignore[attr-defined]

    return user_requested_timestamps

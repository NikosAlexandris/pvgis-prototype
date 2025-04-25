"""
CLI module to calculate the solar zenith angle for a location and a single moment in time.
"""

from datetime import datetime
from pathlib import Path
from typing import Annotated, List
from zoneinfo import ZoneInfo

from pandas import DatetimeIndex

from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.api.position.models import (
    SolarPositionModel,
    SolarPositionParameter,
    SolarTimeModel,
    select_models,
)
from pvgisprototype.api.position.zenith import calculate_solar_zenith_series
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.api.datetime.conversion import convert_timestamps_to_utc
from pvgisprototype.cli.typer.data_processing import (
    typer_option_array_backend,
    typer_option_dtype,
)
from pvgisprototype.cli.typer.earth_orbit import (
    typer_option_eccentricity_amplitude,
    typer_option_eccentricity_phase_offset,
)
from pvgisprototype.cli.typer.location import (
    typer_argument_latitude,
    typer_argument_longitude,
)
from pvgisprototype.cli.typer.output import (
    typer_option_angle_output_units,
    typer_option_csv,
    typer_option_index,
    typer_option_panels_output,
    typer_option_rounding_places,
)
from pvgisprototype.cli.typer.plot import (
    typer_option_uniplot,
    typer_option_uniplot_terminal_width,
)
from pvgisprototype.cli.typer.position import typer_option_solar_position_model
from pvgisprototype.cli.typer.refraction import (
    typer_option_adjust_for_atmospheric_refraction,
)
from pvgisprototype.cli.typer.timestamps import (
    typer_argument_timestamps,
    typer_option_end_time,
    typer_option_frequency,
    typer_option_periods,
    typer_option_random_timestamps,
    typer_option_start_time,
    typer_option_timezone,
)
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.verbosity import typer_option_quiet, typer_option_verbose
from pvgisprototype.cli.typer.validate_output import typer_option_validate_output
from pvgisprototype.constants import (
    ANGLE_OUTPUT_UNITS_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    CSV_PATH_DEFAULT,
    DATA_TYPE_DEFAULT,
    ECCENTRICITY_CORRECTION_FACTOR,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    PERIGEE_OFFSET,
    QUIET_FLAG_DEFAULT,
    RANDOM_TIMESTAMPS_FLAG_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    TERMINAL_WIDTH_FRACTION,
    TIMEZONE_DEFAULT,
    UNIPLOT_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_function_call, logger


@log_function_call
def zenith(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamps: Annotated[DatetimeIndex, typer_argument_timestamps] = str(
        now_utc_datetimezone()
    ),
    start_time: Annotated[
        datetime | None, typer_option_start_time
    ] = None,  # Used by a callback function
    periods: Annotated[
        int | None, typer_option_periods
    ] = None,  # Used by a callback function
    frequency: Annotated[
        str | None, typer_option_frequency
    ] = None,  # Used by a callback function
    end_time: Annotated[
        datetime | None, typer_option_end_time
    ] = None,  # Used by a callback function
    timezone: Annotated[str | None, typer_option_timezone] = TIMEZONE_DEFAULT,
    random_timestamps: Annotated[
        bool, typer_option_random_timestamps
    ] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    model: Annotated[List[SolarPositionModel], typer_option_solar_position_model] = [
        SolarPositionModel.noaa
    ],
    adjust_for_atmospheric_refraction: Annotated[
        bool, typer_option_adjust_for_atmospheric_refraction
    ] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    eccentricity_phase_offset: Annotated[float, typer_option_eccentricity_phase_offset] = PERIGEE_OFFSET,
    eccentricity_amplitude: Annotated[
        float, typer_option_eccentricity_amplitude
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[
        str, typer_option_angle_output_units
    ] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[
        int, typer_option_rounding_places
    ] = ROUNDING_PLACES_DEFAULT,
    group_models: Annotated[
        bool, "Visually cluster time series results per model"
    ] = False,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    resample_large_series: Annotated[bool, "Resample large time series?"] = False,
    terminal_width_fraction: Annotated[
        float, typer_option_uniplot_terminal_width
    ] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    panels: Annotated[bool, typer_option_panels_output] = False,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
    validate_output: Annotated[bool, typer_option_validate_output] = VALIDATE_OUTPUT_DEFAULT,
) -> None:
    """Calculate the solar zenith angle

    The solar zenith angle (SZA) is the angle between the zenith (directly
    overhead) and the line to the sun. A zenith angle of 0 degrees means the
    sun is directly overhead, while an angle of 90 degrees means the sun is on
    the horizon.

    Parameters
    ----------

    Returns
    -------

    """
    utc_timestamps = convert_timestamps_to_utc(
        user_requested_timezone=timezone,
        user_requested_timestamps=timestamps,
    )
    # Why does the callback function `_parse_model` not work?
    solar_position_models = select_models(
        SolarPositionModel, model
    )  # Using a callback fails!
    solar_zenith_series = calculate_solar_zenith_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=utc_timestamps,
        timezone=utc_timestamps.tz,
        solar_position_models=solar_position_models,
        # solar_time_model=solar_time_model,
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        angle_output_units=angle_output_units,
        array_backend=array_backend,
        dtype=dtype,
        verbose=verbose,
        validate_output=validate_output,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    if not quiet:
        from pvgisprototype.cli.print.position import print_solar_position_series_table

        print_solar_position_series_table(
            longitude=longitude,
            latitude=latitude,
            timestamps=utc_timestamps,
            timezone=utc_timestamps.tz,
            table=solar_zenith_series,
            position_parameters=[SolarPositionParameter.zenith],
            title="Solar Zenith Series",
            index=index,
            surface_orientation=None,
            surface_tilt=None,
            incidence=None,
            user_requested_timestamps=timestamps,
            user_requested_timezone=timezone,
            rounding_places=rounding_places,
            group_models=group_models,
            panels=panels,
        )
    if csv:
        from pvgisprototype.cli.write import write_solar_position_series_csv

        write_solar_position_series_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=utc_timestamps,
            timezone=utc_timestamps.tz,
            table=solar_zenith_series,
            # timing=True,
            # declination=True,
            # hour_angle=None,
            zenith=True,
            # altitude=None,
            # azimuth=None,
            # surface_orientation=None,
            # surface_tilt=None,
            # incidence=None,
            user_requested_timestamps=timestamps,
            user_requested_timezone=timezone,
            # rounding_places=rounding_places,
            # group_models=group_models,
            filename=csv,
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_solar_position_series

        uniplot_solar_position_series(
            solar_position_series=solar_zenith_series,
            position_parameters=[SolarPositionParameter.zenith],
            timestamps=utc_timestamps,
            timezone=utc_timestamps.tz,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle="Solar Zenith Series",
            title="Solar Zenith",
            label="Zenith",
            legend_labels=None,
            terminal_width_fraction=terminal_width_fraction,
        )

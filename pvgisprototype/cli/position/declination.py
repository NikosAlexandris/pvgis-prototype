"""
CLI module to calculate the solar declination angle for a location and moment in time.
"""

from pandas import DatetimeIndex
from rich import print
from typing import Annotated
from typing import Optional
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from pvgisprototype.api.position.models import SolarDeclinationModel
from pvgisprototype.api.position.models import select_models

from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.timestamps import typer_option_local_time
from pvgisprototype.cli.typer.position import typer_option_solar_declination_model
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.earth_orbit import typer_option_perigee_offset
from pvgisprototype.cli.typer.earth_orbit import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.verbosity import typer_option_verbose

from pvgisprototype.api.position.declination import calculate_solar_declination_series

from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT, CSV_PATH_DEFAULT, DATA_TYPE_DEFAULT, ECCENTRICITY_CORRECTION_FACTOR, INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT, PERIGEE_OFFSET, QUIET_FLAG_DEFAULT, RADIANS, RANDOM_TIMESTAMPS_FLAG_DEFAULT, TERMINAL_WIDTH_FRACTION, UNIPLOT_FLAG_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_random_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_start_time
from pvgisprototype.cli.typer.timestamps import typer_option_periods
from pvgisprototype.cli.typer.timestamps import typer_option_frequency
from pvgisprototype.cli.typer.timestamps import typer_option_end_time
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.cli.typer.data_processing import typer_option_dtype
from pvgisprototype.cli.typer.data_processing import typer_option_array_backend
from pvgisprototype.cli.typer.plot import typer_option_uniplot
from pvgisprototype.cli.typer.plot import typer_option_uniplot_terminal_width
from pvgisprototype.cli.typer.output import typer_option_csv
from pvgisprototype.cli.typer.verbosity import typer_option_quiet
from pvgisprototype.cli.typer.output import typer_option_index
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.cli.typer.output import typer_option_panels_output


@log_function_call
def declination(
    timestamps: Annotated[DatetimeIndex, typer_argument_timestamps] = str(now_utc_datetimezone()),
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,  # Used by a callback function
    periods: Annotated[Optional[int], typer_option_periods] = None,  # Used by a callback function
    frequency: Annotated[Optional[str], typer_option_frequency] = None,  # Used by a callback function
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,  # Used by a callback function
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    local_time: Annotated[bool, typer_option_local_time] = False,
    random_timestamps: Annotated[bool, typer_option_random_timestamps] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    solar_declination_model: Annotated[List[SolarDeclinationModel], typer_option_solar_declination_model] = [SolarDeclinationModel.pvis],
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    group_models: Annotated[Optional[bool], 'Visually cluster time series results per model'] = False,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    resample_large_series: Annotated[bool, 'Resample large time series?'] = False,
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    panels: Annotated[bool, typer_option_panels_output] = False,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
) -> None:
    """Calculate the solar declination angle 

    The solar declination (delta) is the angle between the line from the Earth
    to the Sun and the plane of the Earth's equator. It varies between ±23.45
    degrees over the course of a year as the Earth orbits the Sun.

    Parameters
    ----------

    Returns
    -------
    solar_declination: float
    """
    # Initialize with None ---------------------------------------------------
    user_requested_timestamps = None
    user_requested_timezone = None
    # -------------------------------------------- Smarter way to do this? ---
    
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamps.tz != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamps = timestamps
        user_requested_timezone = timezone

        timestamps = timestamps.tz_localize(utc_zoneinfo)
        timezone = utc_zoneinfo
        logger.info(f'Input timestamps & zone ({user_requested_timestamps} & {user_requested_timezone}) converted to {timestamps} for all internal calculations!')

    solar_declination_models = select_models(SolarDeclinationModel, solar_declination_model)  # Using a callback fails!
    solar_declination_series = calculate_solar_declination_series(
        timestamps=timestamps,
        timezone=timezone,
        solar_declination_models=solar_declination_models,
        eccentricity_correction_factor=eccentricity_correction_factor,
        perigee_offset=perigee_offset,
        angle_output_units=angle_output_units,
        array_backend=array_backend,
        dtype=dtype,
        verbose=verbose,
    )
    from pvgisprototype.cli.print import print_solar_position_series_table
    if not quiet:
        if timestamps.size == 1:
            if not panels:
                from pvgisprototype.cli.print import print_solar_position_table
                print_solar_position_table(
                    longitude=None,
                    latitude=None,
                    timestamp=timestamps,
                    timezone=timezone,
                    table=solar_declination_series,
                    rounding_places=rounding_places,
                    timing=True,
                    declination=True,
                    hour_angle=None,
                    zenith=None,
                    altitude=None,
                    azimuth=None,
                    surface_orientation=None,
                    surface_tilt=None,
                    incidence=None,  # Add Me ?
                    user_requested_timestamp=user_requested_timestamps, 
                    user_requested_timezone=user_requested_timezone
                )
            else:
                from pvgisprototype.cli.print import print_solar_position_table_panels
                print_solar_position_table_panels(
                    longitude=None,
                    latitude=None,
                    timestamp=timestamps,
                    timezone=timezone,
                    table=solar_declination_series,
                    rounding_places=rounding_places,
                    timing=True,
                    declination=True,
                    hour_angle=None,
                    zenith=None,
                    altitude=None,
                    azimuth=None,
                    incidence=None,  # Add Me ?
                    user_requested_timestamp=user_requested_timestamps, 
                    user_requested_timezone=user_requested_timezone
                )
        else:
            print_solar_position_series_table(
                longitude=None,
                latitude=None,
                timestamps=timestamps,
                timezone=timezone,
                table=solar_declination_series,
                title='Solar Declination Angle',
                index=index,
                timing=True,
                declination=True,
                hour_angle=None,
                zenith=None,
                altitude=None,
                azimuth=None,
                surface_orientation=None,
                surface_tilt=None,
                incidence=None,
                user_requested_timestamps=user_requested_timestamps, 
                user_requested_timezone=user_requested_timezone,
                rounding_places=rounding_places,
                group_models=group_models,
            )
    if csv:
        from pvgisprototype.cli.write import write_solar_position_series_csv
        write_solar_position_series_csv(
            longitude=None,
            latitude=None,
            timestamps=timestamps,
            timezone=timezone,
            table=solar_declination_series,
            timing=True,
            declination=True,
            hour_angle=None,
            zenith=None,
            altitude=None,
            azimuth=None,
            surface_orientation=None,
            surface_tilt=None,
            incidence=None,
            user_requested_timestamps=user_requested_timestamps, 
            user_requested_timezone=user_requested_timezone,
            # rounding_places=rounding_places,
            # group_models=group_models,
            filename=csv,
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_solar_position_series
        uniplot_solar_position_series(
            solar_position_series=solar_declination_series,
            timing=True,
            timestamps=timestamps,
            declination=True,
            # hour_angle=True,
            # zenith=True,
            # altitude=True,
            # azimuth=True,
            # surface_orientation=True,
            # surface_tilt=True,
            # incidence=True,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle='Solar Declination Series',
            title="Solar Declination",
            label='Declination',
            legend_labels=None,
            terminal_width_fraction=terminal_width_fraction,
        )

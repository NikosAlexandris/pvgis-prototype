"""
CLI module to calculate the solar incidence angle for a solar surface at a
location, orientation, tilt and moment in time.
"""

from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pathlib import Path
from typing import Annotated
from typing import Optional
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo

from click.utils import R
from pandas import DatetimeIndex

from pvgisprototype.cli.typer.location import typer_argument_longitude
from pvgisprototype.cli.typer.location import typer_argument_latitude
from pvgisprototype.cli.typer.timestamps import typer_option_random_time
from pvgisprototype.cli.typer.timing import typer_argument_hour_angle
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamp
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.position import typer_option_solar_position_model
from pvgisprototype.cli.typer.refraction import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.earth_orbit import typer_option_perigee_offset
from pvgisprototype.cli.typer.earth_orbit import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer.position import typer_option_solar_incidence_model
from pvgisprototype.cli.typer.position import typer_argument_surface_orientation
from pvgisprototype.cli.typer.position import typer_option_random_surface_orientation
from pvgisprototype.cli.typer.position import typer_argument_surface_tilt
from pvgisprototype.cli.typer.position import typer_option_random_surface_tilt
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.verbosity import typer_option_verbose

from pvgisprototype.api.position.models import SolarPositionModel, SolarPositionParameter
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import select_models

from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT, COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT, CSV_PATH_DEFAULT, DATA_TYPE_DEFAULT, RADIANS, RANDOM_TIMESTAMPS_FLAG_DEFAULT, TERMINAL_WIDTH_FRACTION, UNIPLOT_FLAG_DEFAULT, ZERO_NEGATIVE_SOLAR_INCIDENCE_ANGLES_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT

from math import pi
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.position.incidence import calculate_solar_incidence_series
from pvgisprototype import SurfaceOrientation
from pvgisprototype import SurfaceTilt
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_random_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_start_time
from pvgisprototype.cli.typer.timestamps import typer_option_periods
from pvgisprototype.cli.typer.timestamps import typer_option_frequency
from pvgisprototype.cli.typer.timestamps import typer_option_end_time
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.position import typer_option_sun_to_surface_plane_incidence_angle
from pvgisprototype.cli.typer.output import typer_option_panels_output
from pvgisprototype.cli.typer.verbosity import typer_option_quiet
from pvgisprototype.cli.typer.output import typer_option_index
from pvgisprototype.cli.typer.output import typer_option_csv
from pvgisprototype.constants import QUIET_FLAG_DEFAULT
from pvgisprototype.constants import INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT
from pvgisprototype.cli.typer.data_processing import typer_option_dtype
from pvgisprototype.cli.typer.data_processing import typer_option_array_backend
from pvgisprototype.cli.typer.plot import typer_option_uniplot
from pvgisprototype.cli.typer.plot import typer_option_uniplot_terminal_width
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.cli.typer.output import typer_option_fingerprint
from pvgisprototype.constants import FINGERPRINT_FLAG_DEFAULT
from pvgisprototype.cli.typer.output import typer_option_command_metadata


@log_function_call
def incidence(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    random_surface_orientation: Annotated[Optional[bool], typer_option_random_surface_orientation] = False,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = SURFACE_TILT_DEFAULT,
    random_surface_tilt: Annotated[Optional[bool], typer_option_random_surface_tilt] = False,
    timestamps: Annotated[DatetimeIndex, typer_argument_timestamps] = str(now_utc_datetimezone()),
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,  # Used by a callback function
    periods: Annotated[Optional[int], typer_option_periods] = None,  # Used by a callback function
    frequency: Annotated[Optional[str], typer_option_frequency] = None,  # Used by a callback function
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,  # Used by a callback function
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_timestamps: Annotated[bool, typer_option_random_timestamps] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    solar_incidence_model: Annotated[List[SolarIncidenceModel], typer_option_solar_incidence_model] = [SolarIncidenceModel.iqbal],
    complementary_incidence_angle: Annotated[bool, typer_option_sun_to_surface_plane_incidence_angle] = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.milne,
    zero_negative_solar_incidence_angles: bool = ZERO_NEGATIVE_SOLAR_INCIDENCE_ANGLES_DEFAULT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    group_models: Annotated[Optional[bool], 'Visually cluster time series results per model'] = False,
    # statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    resample_large_series: Annotated[bool, 'Resample large time series?'] = False,
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    metadata: Annotated[bool, typer_option_command_metadata] = False,
    panels: Annotated[bool, typer_option_panels_output] = False,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
):
    """Calculate the angle of solar incidence

    The angle of incidence (also known as theta) is the angle between the
    direct beam of sunlight and the line perpendicular (normal) to the surface.
    If the sun is directly overhead and the surface is flat (horizontal), the
    angle of incidence is 0°.
    """
    # Initialize with None ---------------------------------------------------
    user_requested_timestamps = None
    user_requested_timezone = None
    # -------------------------------------------- Smarter way to do this? ---

    # Convert the input timestamp to UTC, for _all_ internal calculations
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamps.tz != utc_zoneinfo:

       # Note the input timestamp and timezone
        user_requested_timestamps = timestamps
        user_requested_timezone = timezone

        timestamps = timestamps.tz_localize(utc_zoneinfo)
        timezone = utc_zoneinfo
        logger.info(f'Input timestamps & zone ({user_requested_timestamps} & {user_requested_timezone}) converted to {timestamps} for all internal calculations!')

    # --------------------------------------------------------------- Idea ---
    # if not given, optimise tilt and orientation... ?
    # ------------------------------------------------------------------------

    if random_surface_orientation:
        import random
        surface_tilt = random.vonmisesvariate(pi, kappa=0)  # radians

    if random_surface_tilt:
        import random
        surface_tilt = random.uniform(0, pi/2)  # radians

    solar_incidence_models = select_models(SolarIncidenceModel, solar_incidence_model)  # Using a callback fails!
    solar_incidence_series = calculate_solar_incidence_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        surface_orientation=SurfaceOrientation(value=surface_orientation, unit=RADIANS),  # Typer does not easily support custom types !
        surface_tilt=SurfaceTilt(value=surface_tilt, unit=RADIANS),  # Typer does not easily support custom types !
        solar_incidence_models=solar_incidence_models,
        complementary_incidence_angle=complementary_incidence_angle,
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angles,
        # solar_time_model=solar_time_model,
        eccentricity_correction_factor=eccentricity_correction_factor,
        perigee_offset=perigee_offset,
        angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    if not quiet:
        from pvgisprototype.cli.print import print_solar_position_series_table
        print_solar_position_series_table(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            table=solar_incidence_series,
            position_parameters=[SolarPositionParameter.incidence],
            title='Solar Position Overview',
            index=index,
            surface_orientation=None,
            surface_tilt=None,
            incidence=True,
            user_requested_timestamps=user_requested_timestamps, 
            user_requested_timezone=user_requested_timezone,
            rounding_places=rounding_places,
            group_models=group_models,
            panels=panels,
        )
            # from pvgisprototype.cli.print import print_solar_incidence_series_in_columns
            # print_solar_incidence_series_in_columns(
            #         longitude=longitude,
            #         latitude=latitude,
            #         timestamps=timestamps,
            #         timezone=timezone,
            #         table=solar_incidence_series,
            #         )

    if csv:
        from pvgisprototype.cli.write import write_solar_position_series_csv
        write_solar_position_series_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            table=solar_incidence_series,
            timing=None,
            declination=None,
            hour_angle=None,
            zenith=None,
            altitude=None,
            azimuth=None,
            surface_orientation=None,
            surface_tilt=None,
            incidence=True,
            user_requested_timestamps=user_requested_timestamps, 
            user_requested_timezone=user_requested_timezone,
            # rounding_places=rounding_places,
            # group_models=group_models,
            filename=csv,
        )

    if uniplot:
        from pvgisprototype.api.plot import uniplot_solar_position_series
        uniplot_solar_position_series(
            solar_position_series=solar_incidence_series,
            position_parameters=[SolarPositionParameter.incidence],
            timestamps=timestamps,
            surface_orientation=None,
            surface_tilt=None,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle='Solar Position Series',
            title="Solar Position",
            label='Incidence',
            legend_labels=None,
            terminal_width_fraction=terminal_width_fraction,
            verbose=verbose,
        )

from typing import Annotated
from typing import Optional
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo

from pvgisprototype.api.position.models import SolarPositionModel, SolarPositionParameter
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import select_models

from pvgisprototype.cli.typer.location import typer_argument_longitude
from pvgisprototype.cli.typer.location import typer_argument_latitude
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamp
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.position import typer_option_solar_position_model
from pvgisprototype.cli.typer.refraction import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.earth_orbit import typer_option_perigee_offset
from pvgisprototype.cli.typer.earth_orbit import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.verbosity import typer_option_verbose

from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import CSV_PATH_DEFAULT, QUIET_FLAG_DEFAULT, TERMINAL_WIDTH_FRACTION, UNIPLOT_FLAG_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.position.azimuth import calculate_solar_azimuth_series
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import RANDOM_TIMESTAMPS_FLAG_DEFAULT
from pvgisprototype.cli.typer.data_processing import typer_option_dtype
from pvgisprototype.cli.typer.data_processing import typer_option_array_backend
from pvgisprototype.cli.typer.plot import typer_option_uniplot
from pvgisprototype.cli.typer.plot import typer_option_uniplot_terminal_width
from pvgisprototype.cli.typer.output import typer_option_csv
from pvgisprototype.cli.typer.verbosity import typer_option_quiet
from pvgisprototype.cli.typer.output import typer_option_panels_output
from pathlib import Path
from pvgisprototype.constants import CSV_PATH_DEFAULT, QUIET_FLAG_DEFAULT, TERMINAL_WIDTH_FRACTION, UNIPLOT_FLAG_DEFAULT
from pvgisprototype.cli.typer.output import typer_option_index
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamps
from pandas import DatetimeIndex
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.cli.typer.timestamps import typer_option_random_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_start_time
from pvgisprototype.cli.typer.timestamps import typer_option_periods
from pvgisprototype.cli.typer.timestamps import typer_option_frequency
from pvgisprototype.cli.typer.timestamps import typer_option_end_time
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.position import typer_option_solar_position_parameter


@log_function_call
def azimuth(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamps: Annotated[DatetimeIndex, typer_argument_timestamps] = str(now_utc_datetimezone()),
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,  # Used by a callback function
    periods: Annotated[Optional[int], typer_option_periods] = None,  # Used by a callback function
    frequency: Annotated[Optional[str], typer_option_frequency] = None,  # Used by a callback function
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,  # Used by a callback function
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_timestamps: Annotated[bool, typer_option_random_timestamps] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    model: Annotated[List[SolarPositionModel], typer_option_solar_position_model] = [SolarPositionModel.noaa],
    position_parameter: Annotated[List[SolarPositionParameter], typer_option_solar_position_parameter] = [SolarPositionParameter.azimuth],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.milne,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[int, typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
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
) -> float:
    """Calculate the solar azimuth angle.

    The solar azimuth angle (Az) specifies the east-west orientation of the
    sun. It is usually measured from the south, going positive to the west. The
    exact definitions can vary, with some sources defining the azimuth with
    respect to the north, so care must be taken to use the appropriate
    convention.

    Parameters
    ----------

    Returns
    -------
    solar_azimuth: float
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


    solar_position_models = select_models(SolarPositionModel, model)  # Using a callback fails!
    solar_azimuth_series = calculate_solar_azimuth_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_models=solar_position_models,
        solar_time_model=solar_time_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    if not quiet:
        solar_position_parameters = select_models(SolarPositionParameter, position_parameter)  # Using a callback fails!
        if timestamps.size == 1:
            if not panels:
                from pvgisprototype.cli.print import print_solar_position_table
                print_solar_position_table(
                    longitude=longitude,
                    latitude=latitude,
                    timestamp=timestamps,
                    timezone=timezone,
                    table=solar_azimuth_series,
                    rounding_places=rounding_places,
                    position_parameters=solar_position_parameters,
                    surface_orientation=None,
                    surface_tilt=None,
                    incidence=None,  # Add Me ?
                    user_requested_timestamp=user_requested_timestamps, 
                    user_requested_timezone=user_requested_timezone
                )
            else:
                from pvgisprototype.cli.print import print_solar_position_table_panels
                print_solar_position_table_panels(
                    longitude=longitude,
                    latitude=latitude,
                    timestamp=timestamps,
                    timezone=timezone,
                    table=solar_azimuth_series,
                    rounding_places=rounding_places,
                    # timing=True,
                    # declination=None,
                    # hour_angle=None,
                    # zenith=None,
                    # altitude=True,
                    azimuth=True,
                    # incidence=None,  # Add Me ?
                    user_requested_timestamp=user_requested_timestamps, 
                    user_requested_timezone=user_requested_timezone
                )
        else:
            from pvgisprototype.cli.print import print_solar_position_series_table
            print_solar_position_series_table(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                timezone=timezone,
                table=solar_azimuth_series,
                position_parameters=solar_position_parameters,
                title='Solar Azimuth Series',
                index=index,
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
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            table=solar_azimuth_series,
            # timing=True,
            # declination=True,
            # hour_angle=None,
            # zenith=None,
            # altitude=None,
            azimuth=True,
            # surface_orientation=None,
            # surface_tilt=None,
            # incidence=None,
            user_requested_timestamps=user_requested_timestamps, 
            user_requested_timezone=user_requested_timezone,
            # rounding_places=rounding_places,
            # group_models=group_models,
            filename=csv,
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_solar_position_series
        uniplot_solar_position_series(
            solar_position_series=solar_azimuth_series,
            position_parameters=solar_position_parameters,
            timestamps=timestamps,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle='Solar Azimuth Series',
            title="Solar Azimuth",
            label="Azimuth",
            legend_labels=None,
            terminal_width_fraction=terminal_width_fraction,
        )

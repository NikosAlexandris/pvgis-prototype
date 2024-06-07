"""
CLI module to calculate the direct horizontal irradiance component over a
location for a period in time.
"""

import typer
from pvgisprototype.api.irradiance.direct.horizontal import calculate_direct_horizontal_irradiance_series
from pvgisprototype.validation.pvis_data_classes import BaseTimestampSeriesModel
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype import OpticalAirMass
from pathlib import Path
from typing import Annotated
from typing import Optional
from datetime import datetime
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.api.position.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SOLAR_INCIDENCE_ALGORITHM_DEFAULT
from pvgisprototype.cli.typer.location import typer_argument_longitude
from pvgisprototype.cli.typer.location import typer_argument_latitude
from pvgisprototype.cli.typer.location import typer_argument_elevation
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_start_time
from pvgisprototype.cli.typer.timestamps import typer_option_frequency
from pvgisprototype.cli.typer.timestamps import typer_option_end_time
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.irradiance import typer_option_global_horizontal_irradiance
from pvgisprototype.cli.typer.irradiance import typer_option_direct_horizontal_irradiance
from pvgisprototype.cli.typer.time_series import typer_option_mask_and_scale
from pvgisprototype.cli.typer.time_series import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer.time_series import typer_option_tolerance
from pvgisprototype.cli.typer.time_series import typer_option_in_memory
from pvgisprototype.cli.typer.linke_turbidity import typer_option_linke_turbidity_factor_series
from pvgisprototype.cli.typer.refraction import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer.refraction import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer.albedo import typer_option_albedo
from pvgisprototype.cli.typer.irradiance import typer_option_apply_angular_loss_factor
from pvgisprototype.cli.typer.position import typer_option_solar_position_model
from pvgisprototype.cli.typer.position import typer_option_solar_incidence_model
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.earth_orbit import typer_option_solar_constant
from pvgisprototype.cli.typer.earth_orbit import typer_option_perigee_offset
from pvgisprototype.cli.typer.earth_orbit import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.statistics import typer_option_statistics
from pvgisprototype.cli.typer.statistics import typer_option_groupby
from pvgisprototype.cli.typer.output import typer_option_csv
from pvgisprototype.cli.typer.plot import typer_option_uniplot
from pvgisprototype.cli.typer.plot import typer_option_uniplot_terminal_width
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.cli.typer.output import typer_option_index
from pvgisprototype.cli.typer.output import typer_option_fingerprint
from pvgisprototype.cli.typer.verbosity import typer_option_quiet
from pvgisprototype.cli.messages import TO_MERGE_WITH_SINGLE_VALUE_COMMAND
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.constants import IRRADIANCE_UNIT
from pvgisprototype.constants import DIRECT_HORIZONTAL_IRRADIANCE
from pvgisprototype.constants import DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.constants import OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT
import numpy as np
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.progress import progress
from pandas import DatetimeIndex
from rich import print
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.constants import RANDOM_TIMESTAMPS_FLAG_DEFAULT
from pvgisprototype.cli.typer.timestamps import typer_option_random_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_periods
from pvgisprototype.cli.typer.output import typer_option_command_metadata
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import STATISTICS_FLAG_DEFAULT
from pvgisprototype.constants import GROUPBY_DEFAULT
from pvgisprototype.constants import CSV_PATH_DEFAULT
from pvgisprototype.constants import UNIPLOT_FLAG_DEFAULT
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT
from pvgisprototype.constants import QUIET_FLAG_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import FINGERPRINT_FLAG_DEFAULT
from pvgisprototype.constants import METADATA_FLAG_DEFAULT
from pvgisprototype.constants import MINUTES
from pvgisprototype.cli.typer.data_processing import typer_option_dtype
from pvgisprototype.cli.typer.data_processing import typer_option_array_backend


@log_function_call
def get_direct_horizontal_irradiance_series(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamps: Annotated[DatetimeIndex, typer_argument_timestamps] = str(now_utc_datetimezone()),
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    periods: Annotated[Optional[int], typer_option_periods] = None,
    frequency: Annotated[Optional[str], typer_option_frequency] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_timestamps: Annotated[bool, typer_option_random_timestamps] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_position_model: Annotated[SolarPositionModel, typer_option_solar_position_model] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[Optional[str], typer_option_groupby] = GROUPBY_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    resample_large_series: Annotated[bool, 'Resample large time series?'] = False,
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    metadata: Annotated[bool, typer_option_command_metadata] = METADATA_FLAG_DEFAULT,
) -> None:
    """Calculate the direct horizontal irradiance (SID) [W*m-2]

    This function implements the algorithm described by Hofierka [1]_.

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name,
    vol(issue), pages.

    """
    direct_horizontal_irradiance_series = calculate_direct_horizontal_irradiance_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        solar_time_model=solar_time_model,
        solar_position_model=solar_position_model,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
    )
    if not quiet:
        if verbose > 0:
            from pvgisprototype.cli.print import print_irradiance_table_2
            from pvgisprototype.constants import TITLE_KEY_NAME
            print_irradiance_table_2(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                timestamps=timestamps,
                dictionary=direct_horizontal_irradiance_series.components,
                title = (
                    direct_horizontal_irradiance_series.components[TITLE_KEY_NAME]
                        + f" horizontal irradiance series {IRRADIANCE_UNIT}"
                ),
                rounding_places=rounding_places,
                index=index,
                verbose=verbose,
            )
        else:
            flat_list = direct_horizontal_irradiance_series.value.flatten().astype(str)
            csv_str = ','.join(flat_list)
            print(csv_str)

    if statistics:
        from pvgisprototype.api.series.statistics import print_series_statistics
        print_series_statistics(
            data_array=direct_horizontal_irradiance_series.value,
            timestamps=timestamps,
            groupby=groupby,
            title="Direct horizontal irradiance",
            rounding_places=rounding_places,
        )
    if csv:
        from pvgisprototype.cli.write import write_irradiance_csv
        write_irradiance_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=direct_horizontal_irradiance_series.components,
            filename=csv,
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_data_array_series
        uniplot_data_array_series(
            data_array=direct_horizontal_irradiance_series.value,
            list_extra_data_arrays=None,
            timestamps=timestamps,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle = 'Direct Horizontal Irradiance Series',
            title = 'Direct Horizontal Irradiance Series',
            label = 'Direct Horizontal Irradiance',
            extra_legend_labels=None,
            unit = IRRADIANCE_UNIT,
            terminal_width_fraction=terminal_width_fraction,
        )
    if fingerprint:
        from pvgisprototype.cli.print import print_finger_hash
        print_finger_hash(dictionary=direct_horizontal_irradiance_series.components)
    if metadata:
        from pvgisprototype.cli.print import print_command_metadata
        import click
        print_command_metadata(context = click.get_current_context())

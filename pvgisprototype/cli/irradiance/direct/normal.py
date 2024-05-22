"""
CLI module to calculate the direct normal irradiance component over a
location for a period in time.
"""

from typing import Annotated, Optional
from pathlib import Path
from datetime import datetime
import numpy as np
from pandas import DatetimeIndex
from rich import print
from pvgisprototype import OpticalAirMass
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.api.position.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SOLAR_INCIDENCE_ALGORITHM_DEFAULT
from pvgisprototype.api.irradiance.direct.normal import calculate_direct_normal_irradiance_series
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.progress import progress
from pvgisprototype.cli.typer.location import typer_argument_latitude
from pvgisprototype.cli.typer.location import typer_argument_longitude
from pvgisprototype.cli.typer.location import typer_argument_elevation
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamps
# from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.timestamps import typer_option_start_time
from pvgisprototype.cli.typer.timestamps import typer_option_end_time
from pvgisprototype.cli.typer.timestamps import typer_option_frequency
from pvgisprototype.cli.typer.time_series import typer_option_mask_and_scale
from pvgisprototype.cli.typer.time_series import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer.time_series import typer_option_tolerance
from pvgisprototype.cli.typer.time_series import typer_option_in_memory
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.time_series import typer_option_mask_and_scale
from pvgisprototype.cli.typer.time_series import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer.time_series import typer_option_tolerance
from pvgisprototype.cli.typer.time_series import typer_option_in_memory
from pvgisprototype.cli.typer.temperature import typer_argument_temperature_series
from pvgisprototype.cli.typer.wind_speed import typer_argument_wind_speed_series
from pvgisprototype.cli.typer.earth_orbit import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer.earth_orbit import typer_option_solar_constant
from pvgisprototype.cli.typer.earth_orbit import typer_option_perigee_offset
from pvgisprototype.cli.typer.position import typer_option_solar_incidence_model
from pvgisprototype.cli.typer.position import typer_option_solar_position_model
from pvgisprototype.cli.typer.position import typer_option_surface_orientation
from pvgisprototype.cli.typer.position import typer_option_surface_tilt
from pvgisprototype.cli.typer.refraction import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer.refraction import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer.linke_turbidity import typer_option_linke_turbidity_factor
from pvgisprototype.cli.typer.linke_turbidity import typer_option_linke_turbidity_factor_series
from pvgisprototype.cli.typer.optical_air_mass import typer_option_optical_air_mass_series
from pvgisprototype.cli.typer.albedo import typer_option_albedo
from pvgisprototype.cli.typer.photovoltaic import typer_option_photovoltaic_module_model
from pvgisprototype.cli.typer.efficiency import typer_option_pv_power_algorithm
from pvgisprototype.cli.typer.efficiency import typer_option_module_temperature_algorithm
from pvgisprototype.cli.typer.efficiency import typer_option_efficiency
from pvgisprototype.cli.typer.efficiency import typer_option_system_efficiency
from pvgisprototype.cli.typer.spectral_factor import typer_argument_spectral_factor_series
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_angle_units
from pvgisprototype.cli.typer.statistics import typer_option_statistics
from pvgisprototype.cli.typer.statistics import typer_option_groupby
from pvgisprototype.cli.typer.output import typer_option_time_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.output import typer_option_index
from pvgisprototype.cli.typer.output import typer_option_csv
from pvgisprototype.cli.typer.plot import typer_option_uniplot
from pvgisprototype.cli.typer.plot import typer_option_uniplot_terminal_width
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.cli.typer.output import typer_option_fingerprint
from pvgisprototype.cli.typer.verbosity import typer_option_quiet
from pvgisprototype.cli.messages import TO_MERGE_WITH_SINGLE_VALUE_COMMAND
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.constants import OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.constants import DIRECT_HORIZONTAL_IRRADIANCE
from pvgisprototype.constants import DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
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
from pvgisprototype.cli.typer.output import typer_option_command_metadata
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.cli.typer.timestamps import typer_option_periods
from pvgisprototype.constants import RANDOM_TIMESTAMPS_FLAG_DEFAULT
from pvgisprototype.cli.typer.timestamps import typer_option_random_timestamps


@log_function_call
def get_direct_normal_irradiance_series(
    timestamps: Annotated[DatetimeIndex, typer_argument_timestamps] = str(now_utc_datetimezone()),
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,  # Used by a callback function
    periods: Annotated[Optional[int], typer_option_periods] = None,  # Used by a callback function
    frequency: Annotated[Optional[str], typer_option_frequency] = None,  # Used by a callback function
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,  # Used by a callback function
    # timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_timestamps: Annotated[bool, typer_option_random_timestamps] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    optical_air_mass_series: Annotated[OpticalAirMass, typer_option_optical_air_mass_series] = [OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT], # REVIEW-ME + ?
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
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
    # with progress:
    direct_normal_irradiance_series = calculate_direct_normal_irradiance_series(
        timestamps=timestamps,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        optical_air_mass_series=optical_air_mass_series,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
    )
    if not quiet:
        if verbose > 0:
            from pvgisprototype.cli.print import print_irradiance_table_2
            from pvgisprototype.constants import TITLE_KEY_NAME
            print_irradiance_table_2(
                timestamps=timestamps,
                dictionary=direct_normal_irradiance_series.components,
                title = (
                    direct_normal_irradiance_series.components[TITLE_KEY_NAME]
                    + f" normal irradiance series {IRRADIANCE_UNITS}"
                ),
                rounding_places=rounding_places,
                index=index,
                verbose=verbose,
            )
        else:
            flat_list = direct_normal_irradiance_series.value.flatten().astype(str)
            csv_str = ','.join(flat_list)
            print(csv_str)

    if csv:
        from pvgisprototype.cli.write import write_irradiance_csv
        write_irradiance_csv(
            longitude=None,
            latitude=None,
            timestamps=timestamps,
            dictionary=direct_normal_irradiance_series.components,
            filename=csv,
        )
    if statistics:
        from pvgisprototype.api.series.statistics import print_series_statistics
        print_series_statistics(
            data_array=direct_normal_irradiance_series.value,
            timestamps=timestamps,
            groupby=groupby,
            title=f"Direct normal irradiance series {IRRADIANCE_UNITS}",
            rounding_places=rounding_places,
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_data_array_series
        uniplot_data_array_series(
            data_array=direct_normal_irradiance_series.value,
            list_extra_data_arrays=None,
            timestamps=timestamps,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle='Direct Normal Irradiance Series',
            title='Direct Normal Irradiance Series',
            label='Direct Normal Irradiance',
            extra_legend_labels=None,
            unit=IRRADIANCE_UNITS,
            terminal_width_fraction=terminal_width_fraction,
        )
    if fingerprint:
        from pvgisprototype.cli.print import print_finger_hash
        print_finger_hash(dictionary=direct_normal_irradiance_series.components)
    if metadata:
        from pvgisprototype.cli.print import print_command_metadata
        import click
        print_command_metadata(context = click.get_current_context())

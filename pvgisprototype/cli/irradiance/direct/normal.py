"""
CLI module to calculate the direct normal irradiance component over a
location for a period in time.
"""

from datetime import datetime
from pathlib import Path
from typing import Annotated

from pandas import DatetimeIndex, Timestamp
from rich import print

from pvgisprototype import LinkeTurbidityFactor, OpticalAirMass
from pvgisprototype.api.irradiance.direct.normal import (
    calculate_direct_normal_irradiance_series,
)
from pvgisprototype.cli.typer.earth_orbit import (
    typer_option_eccentricity_correction_factor,
    typer_option_perigee_offset,
    typer_option_solar_constant,
)
from pvgisprototype.cli.typer.linke_turbidity import (
    typer_option_linke_turbidity_factor_series,
)
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.cli.typer.optical_air_mass import (
    typer_option_optical_air_mass_series,
)
from pvgisprototype.cli.typer.output import (
    typer_option_command_metadata,
    typer_option_csv,
    typer_option_fingerprint,
    typer_option_index,
    typer_option_rounding_places,
)
from pvgisprototype.cli.typer.plot import (
    typer_option_uniplot,
    typer_option_uniplot_terminal_width,
)
from pvgisprototype.cli.typer.statistics import (
    typer_option_groupby,
    typer_option_statistics,
)

# from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.timestamps import (
    typer_argument_timestamps,
    typer_option_end_time,
    typer_option_frequency,
    typer_option_periods,
    typer_option_random_timestamps,
    typer_option_start_time,
)
from pvgisprototype.cli.typer.verbosity import typer_option_quiet, typer_option_verbose
from pvgisprototype.constants import (
    CSV_PATH_DEFAULT,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    GROUPBY_DEFAULT,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    IRRADIANCE_UNIT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    METADATA_FLAG_DEFAULT,
    OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT,
    PERIGEE_OFFSET,
    QUIET_FLAG_DEFAULT,
    RANDOM_TIMESTAMPS_FLAG_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    SOLAR_CONSTANT,
    STATISTICS_FLAG_DEFAULT,
    TERMINAL_WIDTH_FRACTION,
    UNIPLOT_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_function_call


@log_function_call
def get_direct_normal_irradiance_series(
    timestamps: Annotated[DatetimeIndex | None, typer_argument_timestamps] = str(Timestamp.now('UTC')),
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
    # timezone: Annotated[str | None, typer_option_timezone] = None,
    random_timestamps: Annotated[
        bool, typer_option_random_timestamps
    ] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    linke_turbidity_factor_series: Annotated[
        LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    optical_air_mass_series: Annotated[
        OpticalAirMass, typer_option_optical_air_mass_series
    ] = [
        OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT
    ],  # REVIEW-ME + ?
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[
        float, typer_option_eccentricity_correction_factor
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    rounding_places: Annotated[
        int | None, typer_option_rounding_places
    ] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[str | None, typer_option_groupby] = GROUPBY_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    resample_large_series: Annotated[bool, "Resample large time series?"] = False,
    terminal_width_fraction: Annotated[
        float, typer_option_uniplot_terminal_width
    ] = TERMINAL_WIDTH_FRACTION,
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
            from pvgisprototype.cli.print.irradiance import print_irradiance_table_2
            from pvgisprototype.constants import TITLE_KEY_NAME

            print_irradiance_table_2(
                timestamps=timestamps,
                dictionary=direct_normal_irradiance_series.components,
                title=(
                    direct_normal_irradiance_series.components[TITLE_KEY_NAME]
                    + f" normal irradiance series {IRRADIANCE_UNIT}"
                ),
                rounding_places=rounding_places,
                index=index,
                verbose=verbose,
            )
        else:
            flat_list = direct_normal_irradiance_series.value.flatten().astype(str)
            csv_str = ",".join(flat_list)
            print(csv_str)
    if statistics:
        from pvgisprototype.api.series.statistics import print_series_statistics

        print_series_statistics(
            data_array=direct_normal_irradiance_series.value,
            timestamps=timestamps,
            groupby=groupby,
            title=f"Direct normal irradiance series {IRRADIANCE_UNIT}",
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
            supertitle="Direct Normal Irradiance Series",
            title="Direct Normal Irradiance Series",
            label="Direct Normal Irradiance",
            extra_legend_labels=None,
            unit=IRRADIANCE_UNIT,
            terminal_width_fraction=terminal_width_fraction,
        )
    if fingerprint:
        from pvgisprototype.cli.print.fingerprint import print_finger_hash

        print_finger_hash(dictionary=direct_normal_irradiance_series.components)
    if metadata:
        import click

        from pvgisprototype.cli.print.metadata import print_command_metadata

        print_command_metadata(context=click.get_current_context())
    # Call write_irradiance_csv() last : it modifies the input dictionary !
    if csv:
        from pvgisprototype.cli.write import write_irradiance_csv

        write_irradiance_csv(
            longitude=None,
            latitude=None,
            timestamps=timestamps,
            dictionary=direct_normal_irradiance_series.components,
            filename=csv,
        )

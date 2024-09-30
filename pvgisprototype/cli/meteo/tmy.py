from rich import print
import typer
from typing_extensions import Annotated
from typing import Tuple
from typing import Optional
from pathlib import Path

from pandas import DatetimeIndex
from datetime import datetime

from pvgisprototype.algorithms.tmy.models import FinkelsteinSchaferStatisticModel, TMYStatisticModel
from pvgisprototype.algorithms.tmy.weighting_scheme_model import MeteorologicalVariable
from pvgisprototype.api.quick_response_code import QuickResponseCode
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI
from pvgisprototype.cli.typer.time_series import typer_argument_time_series
from pvgisprototype.cli.typer.location import typer_argument_longitude_in_degrees
from pvgisprototype.cli.typer.location import typer_argument_latitude_in_degrees
from pvgisprototype.cli.typer.timestamps import typer_argument_naive_timestamps
from pvgisprototype.api.datetime.now import now_datetime
from pvgisprototype.cli.typer.timestamps import typer_option_start_time
from pvgisprototype.cli.typer.timestamps import typer_option_periods
from pvgisprototype.cli.typer.timestamps import typer_option_frequency
from pvgisprototype.cli.typer.timestamps import typer_option_end_time
from pvgisprototype.cli.typer.helpers import typer_option_convert_longitude_360
from pvgisprototype.cli.typer.time_series import typer_option_data_variable
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.cli.typer.time_series import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer.time_series import typer_option_tolerance
from pvgisprototype.cli.typer.time_series import typer_option_mask_and_scale
from pvgisprototype.cli.typer.time_series import typer_option_in_memory
from pvgisprototype.cli.typer.statistics import typer_option_statistics
from pvgisprototype.cli.typer.statistics import typer_option_groupby
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.output import typer_option_csv
from pvgisprototype.cli.typer.output import typer_option_output_filename
from pvgisprototype.cli.typer.output import typer_option_variable_name_as_suffix
from pvgisprototype.cli.typer.output import (
    typer_option_angle_output_units,
    typer_option_command_metadata,
    typer_option_csv,
    typer_option_fingerprint,
    typer_option_index,
    typer_option_quick_response,
    typer_option_rounding_places,
)
from pvgisprototype.cli.typer.plot import (
    typer_option_uniplot,
    typer_option_uniplot_terminal_width,
)
from pvgisprototype.cli.typer.verbosity import typer_option_quiet, typer_option_verbose
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.constants import (
    FINGERPRINT_FLAG_DEFAULT,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    LOG_LEVEL_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    NOT_AVAILABLE,
    QUIET_FLAG_DEFAULT,
    RADIANS,
    TERMINAL_WIDTH_FRACTION,
    UNIPLOT_FLAG_DEFAULT,
)
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT
from pvgisprototype.constants import STATISTICS_FLAG_DEFAULT
from pvgisprototype.constants import GROUPBY_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import CSV_PATH_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.algorithms.tmy.tmy import calculate_tmy
from pvgisprototype.algorithms.tmy.weighting_scheme_model import (
    TypicalMeteorologicalMonthWeightingScheme,
)
from pvgisprototype.algorithms.tmy.weighting_scheme_model import (
    TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT,
)


def calculate_degree_days(
    location: Annotated[
        Tuple[float, float], typer.Argument(..., help="Latitude, longitude [°]")
    ],
    years: Annotated[
        Tuple[float, float],
        typer.Argument(
            ..., min=2005, max=2020, help="First and last year of calculations"
        ),
    ],
    meteo: Annotated[
        Path,
        typer.Argument(
            ...,
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
            help="Directory containing the meteorological data",
        ),
    ],
    elevation: Annotated[
        Path,
        typer.Argument(
            ...,
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
            help="Directory containing the digital elevation data",
        ),
    ],
    monthly: bool = typer.Option(False, is_flag=True, help="Print monthly averages"),
):
    """Calculate the cooling/heating degree days

    Args:

    Returns:
        None

    Raises:
        AssertionError: If the command exit code or output doesn't match the expected values.

    Example:

    Notes:
    - Refactored from the original C program `degreedays_hourly` as follows:\n
      - New flag, Old flag, Type, Old Variable, Description\n
      - monthly   , r    , Flag         , -                   , Print monthly averages \n
      - meteo     , g    , str          , dailyPrefix         , Directory containing the meteo files\n
      - elevation , f    , str          , elevationFilename   , Directory prefix of the DEM files\n
      - location  , d    , float, float , latitude, longitude , Latitude, longitude [°]\n
      - years     , y    , float, float , yearStart, yearEnd  , First year, last year of calculations
    """
    pass


def tmy(
    time_series: Annotated[Path, typer_argument_time_series],
    meteorological_variable: Annotated[
        MeteorologicalVariable,
        typer.Argument(help="Standard name of meteorological variable for Finkelstein-Schafer statistics"),
        ],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    # time_series_2: Annotated[Path, typer_option_time_series] = None,
    timestamps: Annotated[DatetimeIndex, typer_argument_naive_timestamps] = str(
        now_datetime()
    ),
    start_time: Annotated[
        Optional[datetime], typer_option_start_time
    ] = None,  # Used by a callback function
    periods: Annotated[
        Optional[int], typer_option_periods
    ] = None,  # Used by a callback function
    frequency: Annotated[
        Optional[str], typer_option_frequency
    ] = None,  # Used by a callback function
    end_time: Annotated[
        Optional[datetime], typer_option_end_time
    ] = None,  # Used by a callback function
    convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    variable: Annotated[Optional[str], typer_option_data_variable] = None,
    neighbor_lookup: Annotated[
        MethodForInexactMatches, typer_option_nearest_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, typer_option_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[Optional[str], typer_option_groupby] = GROUPBY_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    output_filename: Annotated[
        Path, typer_option_output_filename
    ] = "series_in",  # Path(),
    variable_name_as_suffix: Annotated[
        bool, typer_option_variable_name_as_suffix
    ] = True,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    rounding_places: Annotated[
        Optional[int], typer_option_rounding_places
    ] = ROUNDING_PLACES_DEFAULT,
    weighting_scheme: TypicalMeteorologicalMonthWeightingScheme = TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT,
    plot_statistic: Annotated[
        list[TMYStatisticModel],
        typer.Option(help="Select which Finkelstein-Schafer statistics to plot"),
    ] = [TMYStatisticModel.tmy.value],
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
    quick_response_code: Annotated[
        QuickResponseCode, typer_option_quick_response
    ] = QuickResponseCode.NoneValue,
    metadata: Annotated[bool, typer_option_command_metadata] = False,
):
    """Generate the Typical Meteorological Year (TMY)

    A typical meteorological year (TMY) is a set of meteorological data with
    data values for every hour in a year for a given geographical location. The
    data are selected from hourly data in a longer time period (normally 10
    years or more). 
    
    An overview of the algorithm for calculating the TMY :

    1. **Input data** : Read _at least_ 10 years of hourly time series over a
    location

    2. **Daily Statistics** : Compute daily maximum, minimum, and mean for
    selected variables.

    3. **Cumulative Distribution Function** (CDF) : Compute the CDF of each
    variable for each month :

       3.1 one CDF for each variable, month, and year. For example, for the
       Global Horizontal Irradiance (GHI) : one for January 2011, one for
       January 2012 and so on, _and_ for each month the same for the ambient
       Temperature or other variables.
       
       3.2 one long-term CDF for each variable across all years for each month.

    4. **Finkelstein-Schafer Statistic** :

       4.1 Compute the absolute difference between the long-term CDF and the
       candidate month's CDF. 4.2 Compute the weighted sum (WS) of these
       differences for each month and year.

    5. **Typical Months** : Rank months by the lowest WS for each month (e.g.,
    rank all Januaries).

    6. **Month Selection** : 

       - ISO method: Select months based on wind speed similarity to the
         long-term average.

       - Sandia/NREL methods : Re-rank top months by their closeness to
         long-term averages, filtering based on extreme values.

    7. **TMY** : Combine the selected months into a continuous year, smoothing
    variable transitions at month boundaries.

    Notes
    -----

    Pay attention to the default _return_ modus of this function ! Without any
    `--verbose` asked, is to print all TMY variable values as one CSV string.
    In the case of a TMY dataset, this is likely very long.

    """
    tmy = calculate_tmy(
        time_series=time_series,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        start_time=start_time,
        periods=periods,
        frequency=frequency,
        end_time=end_time,
        variable=variable,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        in_memory=in_memory,
        weighting_scheme=weighting_scheme,
        verbose=verbose,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    if quick_response_code.value != QuickResponseCode.NoneValue:
        print(NOT_IMPLEMENTED_CLI)
        # from pvgisprototype.cli.qr import print_quick_response_code

        # print_quick_response_code(
        #     dictionary=tmy,
        #     longitude=longitude,
        #     latitude=latitude,
        #     elevation=False,
        #     surface_orientation=False,
        #     surface_tilt=False,
        #     timestamps=timestamps,
        #     rounding_places=rounding_places,
        # )
    if not quiet:
        if verbose > 0:
            print(NOT_IMPLEMENTED_CLI)
            # from pvgisprototype.cli.print import print_irradiance_table_2

            # print_irradiance_table_2(
            #     longitude=longitude,
            #     latitude=latitude,
            #     timestamps=timestamps,
            #     dictionary=tmy,
            #     # title=photovoltaic_power_output_series['Title'] + f" series {POWER_UNIT}",
            #     rounding_places=rounding_places,
            #     index=index,
            #     surface_orientation=True,
            #     surface_tilt=True,
            #     verbose=verbose,
            # )
        else:
            flat_list = []
            for data_array in tmy.get(
                FinkelsteinSchaferStatisticModel.ranked, NOT_AVAILABLE
            ):
                flat_list.extend(data_array.values.flatten().astype(str))
            csv_str = ",".join(flat_list)
            print(csv_str)
    if csv:
        print(NOT_IMPLEMENTED_CLI)
        # from pvgisprototype.cli.write import write_irradiance_csv

        # write_irradiance_csv(
        #     longitude=longitude,
        #     latitude=latitude,
        #     timestamps=timestamps,
        #     dictionary=tmy,
        #     filename=csv,
        #     index=index,
        # )
    if statistics:
        print(NOT_IMPLEMENTED_CLI)
        # from pvgisprototype.api.series.statistics import print_series_statistics

        # print_series_statistics(
        #     data_array=tmy,
        #     timestamps=timestamps,
        #     groupby=groupby,
        #     title="Typical Meteorological Year",
        # )
    if uniplot:
        print(NOT_IMPLEMENTED_CLI)
        # from pvgisprototype.api.plot import uniplot_data_array_series

        # uniplot_data_array_series(
        #     data_array=tmy[list(tmy.data_vars)[0]],
        #     # list_extra_data_arrays=individual_series,
        #     timestamps=timestamps,
        #     resample_large_series=resample_large_series,
        #     lines=True,
        #     supertitle="Typical Meteorological Year",
        #     title="Typical Meteorological Year",
        #     label="TMY",
        #     # extra_legend_labels=individual_labels,
        #     unit="?",
        #     terminal_width_fraction=terminal_width_fraction,
        # )
    if plot_statistic:
        from typing import List
        from pvgisprototype.algorithms.tmy.models import select_models

        def plot_requested_tmy_statistics(
            tmy_series: dict,
            statistics: List[TMYStatisticModel],
            weighting_scheme: str = "",
        ):
            """Plot the selected models based on the Enum to function mapping."""
            from pvgisprototype.algorithms.tmy.models import PLOT_FUNCTIONS

            for statistic in statistics:
                if statistic == TMYStatisticModel.tmy:
                    plot_function = PLOT_FUNCTIONS.get(statistic)
                    plot_function(
                        tmy_series=tmy_series.get(statistic.value),
                        finkelstein_schafer_statistic=tmy_series.get(
                            "Finkelstein-Schafer"
                        ),
                        typical_months=tmy_series.get("Typical months"),
                        input_series=tmy_series.get("Input time series"),
                        # title=TMYStatisticModel.tmy.name,
                        title="Typical Meteorological Year",
                        weighting_scheme=weighting_scheme,
                        fingerprint=fingerprint,
                    )
                elif statistic == TMYStatisticModel.ranked:
                    plot_function = PLOT_FUNCTIONS.get(statistic.value)
                    plot_function(
                        ranked_finkelstein_schafer_statistic=tmy_series.get(statistic.value),
                        weighting_scheme=weighting_scheme,
                    )
                else:
                    plot_function = PLOT_FUNCTIONS.get(statistic.value)
                    plot_function(
                            tmy_series.get(statistic.value, None),
                            )

        tmy_statistics = select_models(
            enum_type=TMYStatisticModel,
            models=plot_statistic,
        )
        plot_requested_tmy_statistics(
            tmy_series=tmy,
            statistics=tmy_statistics,
            weighting_scheme=weighting_scheme.name,
        )
    if fingerprint:
        print(NOT_IMPLEMENTED_CLI)
        # from pvgisprototype.cli.print import print_finger_hash

        # print_finger_hash(dictionary=tmy[list(tmy.data_vars)[0]])
    if metadata:
        import click

        from pvgisprototype.cli.print import print_command_metadata

        print_command_metadata(context=click.get_current_context())

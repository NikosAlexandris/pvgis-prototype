import typer
from typing_extensions import Annotated
from typing import Tuple
from typing import Optional
from pathlib import Path

from pandas import DatetimeIndex
from datetime import datetime
from pvgisprototype.cli.typer.time_series import typer_argument_time_series
from pvgisprototype.cli.typer.time_series import typer_option_time_series
from pvgisprototype.cli.typer.location import typer_argument_longitude
from pvgisprototype.cli.typer.location import typer_argument_longitude_in_degrees
from pvgisprototype.cli.typer.location import typer_argument_latitude
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
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.constants import NEIGHBOR_LOOKUP_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT
from pvgisprototype.constants import STATISTICS_FLAG_DEFAULT
from pvgisprototype.constants import GROUPBY_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import CSV_PATH_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.algorithms.tmy.tmy import calculate_tmy
from pvgisprototype.algorithms.tmy.weighting_scheme_model import TypicalMeteorologicalMonthWeightingScheme
from pvgisprototype.algorithms.tmy.weighting_scheme_model import get_typical_meteorological_month_weighting_scheme
from pvgisprototype.algorithms.tmy.weighting_scheme_model import TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT


def calculate_degree_days(
        location: Annotated[Tuple[float, float], typer.Argument(..., help='Latitude, longitude [°]')],
        years: Annotated[Tuple[float, float], typer.Argument(..., min=2005, max=2020, help='First and last year of calculations')],
        meteo: Annotated[Path, typer.Argument( ..., exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True, help='Directory containing the meteorological data',)],
        elevation: Annotated[Path, typer.Argument( ..., exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True, help='Directory containing the digital elevation data')],
        monthly: bool = typer.Option(False, is_flag=True, help='Print monthly averages'),
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


# @app.command('tmy')
def tmy(
    time_series: Annotated[Path, typer_argument_time_series],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    # time_series_2: Annotated[Path, typer_option_time_series] = None,
    timestamps: Annotated[DatetimeIndex, typer_argument_naive_timestamps] = str(now_datetime()),
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,  # Used by a callback function
    periods: Annotated[Optional[int], typer_option_periods] = None,  # Used by a callback function
    frequency: Annotated[Optional[str], typer_option_frequency] = None,  # Used by a callback function
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,  # Used by a callback function
    convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    variable: Annotated[Optional[str], typer_option_data_variable] = None,
    neighbor_lookup: Annotated[MethodForInexactMatches, typer_option_nearest_neighbor_lookup] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[Optional[str], typer_option_groupby] = GROUPBY_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    output_filename: Annotated[Path, typer_option_output_filename] = 'series_in',  #Path(),
    variable_name_as_suffix: Annotated[bool, typer_option_variable_name_as_suffix] = True,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    weighting_scheme: TypicalMeteorologicalMonthWeightingScheme = TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT,
    log: Annotated[int, typer_option_log] = VERBOSE_LEVEL_DEFAULT,
    plot: bool = False,
):
    """Generate the Typical Meteorological Year

    A typical meteorological year (TMY) is a set of meteorological data with
    data values for every hour in a year for a given geographical location. The
    data are selected from hourly data in a longer time period (normally 10
    years or more). The TMY tool can be used to interactively visualise all the
    data or to download the data as a text file.
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
        plot=plot,
    )
    print(f'{tmy=}')

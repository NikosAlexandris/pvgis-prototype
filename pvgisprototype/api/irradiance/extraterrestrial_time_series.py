from devtools import debug
import typer
from typing import Annotated
from typing import Optional
from datetime import datetime
# from pvgisprototype.cli.typer_parameters import typer_argument_timestamps
from pvgisprototype.cli.typer_parameters import typer_option_timestamps
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_frequency
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_solar_constant
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.cli.typer_parameters import typer_option_random_days
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import IRRADIANCE_UNITS
import numpy as np
from pvgisprototype.cli.print import print_irradiance_table_2
# from pvgisprototype.api.utilities.timestamp import get_days_in_year


app = typer.Typer(
    # cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Calculate the extraterrestrial normal irradiance over a time series",
)


def get_days_per_year(years):
    return 365 + ((years % 4 == 0) & ((years % 100 != 0) | (years % 400 == 0))).astype(int)


@app.callback(
    'extraterrestrial-series',
    invoke_without_command=True,
    no_args_is_help=True,
    help=f"Calculate the extraterrestrial normal irradiance over a time series",
)
def calculate_extraterrestrial_normal_irradiance_time_series(
    # timestamps: Annotated[datetime, typer_argument_timestamps],
    timestamps: Annotated[datetime, typer_option_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    frequency: Annotated[Optional[str], typer_option_frequency] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    random_days: Annotated[bool, typer_option_random_days] = RANDOM_DAY_SERIES_FLAG_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
) -> np.ndarray:
    """ """
    timestamps = np.array(timestamps)
    years_in_timestamps = timestamps.astype('datetime64[Y]').astype(int) + 1970
    years, indices = np.unique(years_in_timestamps, return_inverse=True)
    days_per_year = get_days_per_year(years)
    days_in_years = days_per_year[indices]

    if random_days:
        day_of_year_series = np.random.randint(1, days_in_years + 1)
    else:
        start_of_years = np.datetime64('1970-01-01').astype('datetime64[D]').astype(int) + 365 * (years - 1970) + (years // 4 - 1970 // 4)
        start_of_timestamp_years = start_of_years[indices]
        day_of_year_series = (timestamps.astype('datetime64[D]').astype(int) - start_of_timestamp_years) + 1

    position_of_earth_series = 2 * np.pi * day_of_year_series / days_in_years
    distance_correction_factor_series = 1 + eccentricity_correction_factor * np.cos(position_of_earth_series - perigee_offset)
    extraterrestrial_normal_irradiance_series = solar_constant * distance_correction_factor_series

    if verbose == 3:
        debug(locals())

    results = {
        "Extraterrestrial": extraterrestrial_normal_irradiance_series
    }

    if verbose > 1:
        extended_results = {
            "Day of year": day_of_year_series,
            "Distance correction": distance_correction_factor_series,
        }
        results = results | extended_results

    print_irradiance_table_2(
        longitude=None,
        latitude=None,
        timestamps=timestamps,
        dictionary=results,
        title=f'Extraterrestrial normal irradiance series {IRRADIANCE_UNITS}',
        rounding_places=rounding_places,
        verbose=verbose,
    )

    return extraterrestrial_normal_irradiance_series

import typer
from typing import Annotated
from typing import Optional
from datetime import datetime
from pvgisprototype.api.irradiance.extraterrestrial_time_series import calculate_extraterrestrial_normal_irradiance_time_series
from pvgisprototype.cli.typer_parameters import typer_argument_timestamps
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_frequency
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_solar_constant
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer_parameters import typer_option_random_days
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.cli.typer_parameters import typer_option_index
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.cli.print import print_irradiance_table_2
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import IRRADIANCE_UNITS


app = typer.Typer(
    # cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Calculate the extraterrestrial normal irradiance over a time series",
)


@app.callback(
    'extraterrestrial-series',
    invoke_without_command=True,
    no_args_is_help=True,
    help=f"Calculate the extraterrestrial normal irradiance over a time series",
)
def get_extraterrestrial_normal_irradiance_time_series(
    timestamps: Annotated[datetime, typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    frequency: Annotated[Optional[str], typer_option_frequency] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    random_days: Annotated[bool, typer_option_random_days] = RANDOM_DAY_SERIES_FLAG_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = False,
) -> None:
    """ """
    results = calculate_extraterrestrial_normal_irradiance_time_series(
        timestamps=timestamps,
        start_time=start_time,
        frequency=frequency,
        end_time=end_time,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        random_days=random_days,
        verbose=verbose,
    )
    if verbose > 0:
        print_irradiance_table_2(
            longitude=None,
            latitude=None,
            timestamps=timestamps,
            dictionary=results,
            title=results['Title'] + f'Extraterrestrial normal irradiance series {IRRADIANCE_UNITS}',
            rounding_places=rounding_places,
            index=index,
            verbose=verbose,
        )
    else:
        print(results)


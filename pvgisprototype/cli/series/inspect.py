from pathlib import Path
from pvgisprototype.api.series.open import read_data_array_or_set
from typing_extensions import Annotated
from pvgisprototype.cli.typer.time_series import (
    typer_argument_time_series,
)
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.constants import (
    VERBOSE_LEVEL_DEFAULT,
)


def inspect_xarray_supported_data(
    time_series: Annotated[Path, typer_argument_time_series],
    encodings: bool = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Select location series"""
    time_series_xarray = read_data_array_or_set(
            input_data=time_series,
            verbose=verbose,
    )
    print(time_series_xarray)

    if encodings:
        print(time_series_xarray.encoding)

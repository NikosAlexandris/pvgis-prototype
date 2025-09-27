#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
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

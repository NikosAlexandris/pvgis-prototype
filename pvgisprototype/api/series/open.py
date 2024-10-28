# from pvgisprototype.api.series.hardcodings import check_mark, exclamation_mark, x_mark
# from pvgisprototype.log import logger
from pathlib import Path
# from typing import Tuple
from pvgisprototype.api.series.utilities import read_data_array_or_set
# from pvgisprototype.constants import NOT_AVAILABLE
# from xarray import open_dataset as xarray_open_dataset
# from humanize import naturalsize
# from xarray import Dataset, DataArray
from typing_extensions import Annotated
# from pvgisprototype.cli.typer.location import (
#     typer_argument_latitude_in_degrees,
#     typer_argument_longitude_in_degrees,
# )
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.cli.typer.time_series import (
    typer_argument_time_series,
    # typer_option_data_variable,
)
# from pvgisprototype.cli.typer.spectral_responsivity import (
    # typer_option_wavelength_column_name,
# )
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.constants import (
    VERBOSE_LEVEL_DEFAULT,
)
# from .models import (
#     XarrayVariableSet,
#     select_netcdf_variable_set_from_dataset,
#     select_xarray_variable_set_from_dataset,
# )


def open_xarray_supported_time_series_data(
    time_series: Annotated[Path, typer_argument_time_series],
    # longitude: Annotated[float, typer_argument_longitude_in_degrees],
    # latitude: Annotated[float, typer_argument_latitude_in_degrees],
    # variable: Annotated[str | None, typer_option_data_variable] = None,
    # coordinate: Annotated[
    #     str,
    #     typer_option_wavelength_column_name,  # Update Me
    # ] = None,
    encodings: bool = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[int, typer_option_log] = VERBOSE_LEVEL_DEFAULT,
):
    """Select location series"""
    # output_handlers = {
    #     ".nc": lambda time_series, path: time_series.to_netcdf(path),
    # }
    # time_series_xarray = open_time_series(
    #     time_series=time_series,
    #     variable=variable,
    #     coordinate=coordinate,
    #     verbose=verbose,
    #     log=log,
    # )
    time_series_xarray = read_data_array_or_set(
            input_data=time_series,
            # mask_and_scale=mask_and_scale,
            # in_memory=in_memory,
            verbose=verbose,
            # log=log,
    )
    # if isinstance(time_series_xarray, Dataset):
    #     if not variable:
    #         raise ValueError("You must specify a variable when selecting from a Dataset.")
    #     if variable not in time_series_xarray:
    #         raise ValueError(f"Variable '{variable}' not found in the Dataset.")
    #     time_series_array = time_series_xarray[variable]  # Extract the DataArray from the Dataset
    #     logger.info(
    #             f"  {check_mark} Successfully extracted '{variable}' from '{time_series_xarray.name}'.",
    #             alt=f"  {check_mark} [green]Successfully[/green] extracted '{variable}' from '{time_series_xarray.name}'."
    #             )

    # elif isinstance(time_series_xarray, DataArray):
    #     time_series_array = time_series_xarray  # It's already a DataArray, use it directly
    
    # else:
    #     raise ValueError("Unsupported data type. Must be a DataArray or Dataset.")

    #if not variable:
    #    dataset = xarray_open_dataset(time_series)
    #    # ----------------------------------------------------- Review Me ----    
    #    #
    #    if len(dataset.data_vars) >= 2:
    #        variables = list(dataset.data_vars.keys())
    #        print(f"The dataset contains more than one variable : {variables}")
    #        variable = typer.prompt(
    #            "Please specify the variable you are interested in from the above list"
    #        )
    #    else:
    #        variable = list(dataset.data_vars)
    #    #
    #    # ----------------------------------------------------- Review Me ----    

    print(time_series_xarray)

    if encodings:
        print(time_series_xarray.encoding)

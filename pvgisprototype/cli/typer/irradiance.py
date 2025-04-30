"""
Solar irradiance
"""

from numpy import fromstring, ndarray
from numpy.typing import NDArray
import typer
from pathlib import Path
from pandas import Series, DataFrame, read_csv
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_advanced_options,
    rich_help_panel_irradiance_series,
    rich_help_panel_spectrum,
)


global_horizontal_irradiance_typer_help = (
    "Global horizontal irradiance (Surface Incoming Shortwave Irradiance (SIS), `ssrd`"
)
direct_horizontal_irradiance_typer_help = "Direct (or beam) horizontal irradiance (Surface Incoming Direct radiation (SID), `fdir`"
the_term_n_unit = "unitless"
the_term_n_series_typer_help = (
    f"The term N for the calculation of the sky dome fraction viewed by a tilted surface for a period of time [{the_term_n_unit}]",
)


def parse_irradiance_series(
    irradiance_input: int | str | Path,
) -> int | str | Path | ndarray | None:
    """
    Notes
    -----
    FIXME: Re-design ?

    """
    try:
        if isinstance(irradiance_input, int):
            return irradiance_input

        if isinstance(irradiance_input, (str, Path)):
            path = Path(irradiance_input)
            if path.exists():
                return path

        if isinstance(irradiance_input, str):
            irradiance_input_array = fromstring(irradiance_input, sep=",")
            if irradiance_input_array.size > 0:
                return irradiance_input_array
            else:
                raise ValueError(
                    f"The input string '{irradiance_input}' could not be parsed into valid solar irradiance values."
                )

    except ValueError as e:  # conversion to float failed
        raise ValueError(
                f"Error parsing input: {e}"
        )


def parse_irradiance_data(irradiance: str) -> Series | DataFrame:
    """
    Parse irradiance data from a CSV file and return a pandas DataFrame
    with a DatetimeIndex.

    Parameters
    ----------
    file_path : str or Path
        The path to the CSV file containing the irradiance data.

    Returns
    -------
    DataFrame
        A Pandas DataFrame with a DatetimeIndex and irradiance data.

    """
    if isinstance(irradiance, str) and Path(irradiance).exists():
        return Path(irradiance)
    else:
        print(f'Implement a parser to process the string and return eventually a Pandas DataFrame or a NumPy array structure ?')


def is_csv(file_path: Path) -> bool:
    return file_path.suffix == '.csv'


def is_netcdf(file_path: Path) -> bool:
    return file_path.suffix in {'.nc', '.netcdf'}


def callback_irradiance_data(
    ctx: typer.Context,
    irradiance: Path,
) -> DataFrame | NDArray:
    """
    """
    if isinstance(irradiance, Path):
        if is_csv(irradiance):
            irradiance_dataframe = read_csv(
                    irradiance,
                    index_col=0,
                    parse_dates=True,
                    dtype=float,
            )
            if not isinstance(irradiance.columns, float):
                irradiance_dataframe.columns = irradiance_dataframe.columns.astype(float)

            return irradiance_dataframe

        
        elif is_netcdf(irradiance):
            return irradiance

        else:
            raise ValueError("Unsupported file format. Only CSV and NetCDF are supported.")
    
    raise ValueError("Unsupported input type for irradiance data.")


spectral_irradiance_wavelength_limit_typer_help = (
    "wavelength for spectral irradiance range"
)
typer_option_minimum_spectral_irradiance_wavelength = typer.Option(
    help=f"Minimum {spectral_irradiance_wavelength_limit_typer_help}",
    is_eager=True,
    rich_help_panel=rich_help_panel_spectrum,
)
typer_option_maximum_spectral_irradiance_wavelength = typer.Option(
    help="Maximum {spectral_irradiance_wavelength_limit_typer_help}",
    is_eager=True,
    rich_help_panel=rich_help_panel_spectrum,
)
typer_argument_irradiance_series = typer.Argument(
    help="Irradiance series",
    parser=parse_irradiance_series,
    rich_help_panel=rich_help_panel_irradiance_series,
    show_default=False,
    is_eager=True,
)
typer_argument_global_horizontal_irradiance = typer.Argument(
    help=global_horizontal_irradiance_typer_help,
    rich_help_panel=rich_help_panel_irradiance_series,
    show_default=False,
)
typer_argument_spectrally_resolved_irradiance = typer.Argument(
    help="",
    parser=parse_irradiance_data,
    rich_help_panel=rich_help_panel_spectrum,
    is_eager=True,
)
typer_option_global_horizontal_irradiance = typer.Option(
    help=global_horizontal_irradiance_typer_help,
    rich_help_panel=rich_help_panel_irradiance_series,
    is_eager=True,
    show_default=False,
)
typer_argument_direct_horizontal_irradiance = typer.Argument(
    help=direct_horizontal_irradiance_typer_help,
    rich_help_panel=rich_help_panel_irradiance_series,
    show_default=False,
)
typer_option_direct_horizontal_irradiance = typer.Option(
    help=direct_horizontal_irradiance_typer_help,
    rich_help_panel=rich_help_panel_irradiance_series,
    is_eager=True,
    show_default=False,
)
typer_argument_term_n = typer.Argument(
    help=the_term_n_series_typer_help,
    show_default=False,
)
typer_argument_term_n_series = typer.Argument(
    help=the_term_n_series_typer_help,
    show_default=False,
)
typer_option_apply_reflectivity_factor = typer.Option(
    help="Apply angular loss function",
    rich_help_panel=rich_help_panel_advanced_options,
)
typer_option_extraterrestrial_normal_irradiance = typer.Option(
    help="",
    parser=parse_irradiance_data,
    rich_help_panel=rich_help_panel_spectrum,
    is_eager=True,
)

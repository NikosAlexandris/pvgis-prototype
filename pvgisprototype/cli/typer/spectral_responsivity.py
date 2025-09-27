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
"""
Spectral Responsivity
"""

from pvgisprototype.log import logger
from pvgisprototype.api.spectrum.helpers_pelland import (
    adjust_band_limits,
    generate_banded_data,
)
from pvgisprototype.api.irradiance.kato_bands import KATO_BANDS
from pathlib import Path
from pandas import read_csv, Series, DataFrame
import typer
from pvgisprototype.constants import (
    RESPONSIVITY_SPECTRAL_DATA,
    SPECTRAL_RESPONSIVITY_CSV_COLUMN_NAME_DEFAULT,
    WAVELENGTHS_CSV_COLUMN_NAME_DEFAULT,
)
from pvgisprototype.api.spectrum.models import (
    PhotovoltaicModuleSpectralResponsivityModel,
    SpectralMismatchModel,
)
from pvgisprototype import SpectralFactorSeries, SpectralResponsivity
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_spectral_responsivity,
    rich_help_panel_time_series_data_selection,
)


spectral_responsivity_typer_help = "Spectral responsivity of a photovoltaic device expressed in units A/W (amperes per watt) is the electrical current (in amperes) per unit of incident optical power (in watts) at specific wavelengths (CSV string or file, examples: 'path_to_file.csv' or '400,0.3; 500,0.5; 600,0.2')"


# PhotovoltaicModuleType

photovoltaic_module_type_typer_help = "Photovoltaic module type for the spectral responsivity. [yellow]Column names in CSV input [bold]must match[/bold] this option's listed types![/yellow]"
typer_option_photovoltaic_module_type = typer.Option(
    help=photovoltaic_module_type_typer_help,
    is_eager=True,
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_spectral_responsivity,
)

# Responsivity


def parse_spectral_responsivity(
    # ctx: typer.Context,
    spectral_responsivity_input: None | str,
    # ) -> SpectralResponsivity:
):
    """Parse spectral responsivity data from either a CSV file or string.

    Notes
    -----
    The CSV string should be ...

    """
    # wavelengths_series_index_name = ctx.params.get("wavelengths_column")
    wavelength_series_index_name = WAVELENGTHS_CSV_COLUMN_NAME_DEFAULT
    # responsivity_label = ctx.params.get("responsivity_column")
    responsivity_label = SPECTRAL_RESPONSIVITY_CSV_COLUMN_NAME_DEFAULT

    if isinstance(spectral_responsivity_input, dict):
        spectral_responsivity_dataframe = DataFrame(
            spectral_responsivity_input,
        )
        import pandas.api.types as ptypes

        if ptypes.is_numeric_dtype(spectral_responsivity_dataframe.index):
            spectral_responsivity_dataframe.index.name = "Wavelength"
            spectral_responsivity_dataframe.reset_index().set_index("Wavelength")
        else:
            spectral_responsivity_dataframe.index.name = "Type"
            spectral_responsivity_dataframe.reset_index().set_index("Type")
        return spectral_responsivity_dataframe

    elif (
        isinstance(spectral_responsivity_input, str)
        and Path(spectral_responsivity_input).exists()
    ):
        logger.debug(
            f"Reading spectral responsivity data from '{spectral_responsivity_input}'",
            alt=f"[bold]Reading[/bold] [green]spectral responsivity[/green] data from '{spectral_responsivity_input}'",
        )
        spectral_responsivity = read_csv(
            filepath_or_buffer=spectral_responsivity_input,
            index_col=0,
        )
        import pandas.api.types as ptypes

        if ptypes.is_numeric_dtype(spectral_responsivity.index):
            spectral_responsivity.index.name = "Wavelength"
            spectral_responsivity.reset_index().set_index("Wavelength")
        else:
            spectral_responsivity.index.name = "Type"
            spectral_responsivity.reset_index().set_index("Type")

        logger.debug(
            f"Spectral responsivity input data (of type {type(spectral_responsivity)}) : \n{spectral_responsivity}",
            alt=f"[green]Spectral responsivity[/green] input data (of type {type(spectral_responsivity)}) :\n{spectral_responsivity}",
        )
        # Check if required columns are present
        # required_index = 'Wavelength [nm]'
        # if not required_index == spectral_responsivity.index.name:
        #     raise ValueError(f"CSV file must contain the column: {required_index}")

        return spectral_responsivity

    elif isinstance(spectral_responsivity_input, str):
        # Parse string input
        logger.debug(
            f"Parsing spectral responsivity data from '{spectral_responsivity_input}'",
            alt=f"[bold]Parsing[/bold] [green]spectral responsivity[/green] data from '{spectral_responsivity_input}'",
        )
        try:
            pairs = spectral_responsivity_input.split(";")
            wavelengths = []
            responsivities = []
            for pair in pairs:
                wavelength, responsivity = map(float, pair.split(","))
                wavelengths.append(wavelength)
                responsivities.append(responsivity)
            wavelengths = np.array(wavelengths)
            responsivities = np.array(responsivities)
            spectral_responsivity = Series(responsivities).set_index(wavelengths)

        except ValueError as e:
            raise ValueError(
                "The `responsivity` input string must be in the format 'wavelength1,responsivity1; wavelength2,responsivity2; ...'"
            ) from e

    else:
        raise TypeError(
            "Input for responsivity must be either a Path to or a properly formatted CSV string."
        )

    # return SpectralResponsivity(
    #         value=responsivities,
    #         wavelengths=wavelengths,
    #         )
    return spectral_responsivity


def resolve_spectral_responsivity():
    """ """
    # generate_banded_data(adjusted_bands, spectral_responsivity.T, 'responsivity')
    pass


def callback_spectral_responsivity_pandas(
    ctx: typer.Context,
    spectral_responsivity_input: DataFrame,
) -> DataFrame:
    """
    Parse spectral responsivity data from a CSV file and return a Pandas Series.

    Parameters
    ----------
    spectral_responsivity_input : DataFrame
        The input data for spectral responsivity. It must be a path to a well
        structured CSV file.

    Returns
    -------
    Series
        A Pandas Series with wavelength values as the index and responsivity values as the data.

    Notes
    -----
    The CSV file must contain 'Wavelength [nm]' and 'Spectral Response [A/W]' columns.
    If the input is a string, it must be in the format 'wavelength1,responsivity1; wavelength2,responsivity2; ...'
    """
    # Select photovoltaic module types

    photovoltaic_module_type = list(ctx.params.get("photovoltaic_module_type"))
    from pvgisprototype.api.position.models import select_models

    photovoltaic_module_types = select_models(
        PhotovoltaicModuleSpectralResponsivityModel, photovoltaic_module_type
    )  # Using a callback fails!
    logger.debug(
        f"Requested photovoltaic module types : {photovoltaic_module_types}",
        alt=f"Requested [purple]photovoltaic module[/purple] types : {photovoltaic_module_types}",
    )

    # input is a DataFrame with multiple photovoltaic module types

    if isinstance(spectral_responsivity_input, DataFrame):

        # Case 1 : Each photovoltaic module type is a column in the DataFrame

        if photovoltaic_module_types and all(
            module in spectral_responsivity_input.columns
            for module in photovoltaic_module_types
        ):
            logger.debug(
                f"Retrieving spectral responsivity data for : {photovoltaic_module_types}",
                alt=f"[bold]Retrieving[/bold] [green]spectral responsivity[/green] data for : [purple]{photovoltaic_module_types}[/purple]",
            )
            spectral_responsivity_input = spectral_responsivity_input[
                photovoltaic_module_types
            ].T  # Why Transpose ?

        # Case 2 : Each photovoltaic module type is a row in the DataFrame's index

        elif photovoltaic_module_types and all(
            module in spectral_responsivity_input.index
            for module in photovoltaic_module_types
        ):
            logger.debug(
                f"Retrieving spectral responsivity data (from .index) for : {photovoltaic_module_types}"
            )
            spectral_responsivity_input = spectral_responsivity_input[
                photovoltaic_module_types
            ]

        # Else, default to cSi

        elif not photovoltaic_module_types or photovoltaic_module_types == [
            PhotovoltaicModuleSpectralResponsivityModel.cSi
        ]:
            spectral_responsivity_input = spectral_responsivity_input[
                PhotovoltaicModuleSpectralResponsivityModel.cSi
            ]

        else:
            logger.error(
                f"Module type '{photovoltaic_module_types}' not found in spectral responsivity data."
            )
            raise KeyError(
                f"Module type '{photovoltaic_module_types}' not found in spectral responsivity data."
            )

    # input is a Series with a single photovoltaic module type

    elif isinstance(spectral_responsivity_input, Series):
        if photovoltaic_module_types and photovoltaic_module_types != [
            PhotovoltaicModuleSpectralResponsivityModel.cSi
        ]:
            logger.error(
                f"Module type '{photovoltaic_module_types}' not applicable. Input data is already a Series."
            )
            raise KeyError(
                f"Module type '{photovoltaic_module_types}' not applicable. Input data is already a Series."
            )

    else:
        raise TypeError("Input for responsivity must be either a DataFrame or Series.")

    # adjust input spectral limits to match the Kato bands.

    min_wavelength = float(ctx.params.get("min_wavelength"))
    max_wavelength = float(ctx.params.get("max_wavelength"))
    adjusted_bands = adjust_band_limits(
        DataFrame(KATO_BANDS),
        min_wavelength=min_wavelength,
        max_wavelength=max_wavelength,
    )

    # How to check if not banded ?

    integrate_responsivity = ctx.params.get("integrate_responsivity")
    if integrate_responsivity:
        logger.debug(
            f"Parameter `integrate_responsivity` set to {integrate_responsivity}"
        )
        logger.debug(
            f":information: Banding spectral responsivity input",
            alt=f":information: [bold][magenta]Banding[/magenta] spectral responsivity input[/bold]",
        )
        spectrally_resolved_responsivity = generate_banded_data(
            reference_bands=adjusted_bands,
            spectral_data=spectral_responsivity_input,  # ).T,  # DataFrame Required !  Why Transpose ?
            data_type=RESPONSIVITY_SPECTRAL_DATA,
        )
        logger.debug(
            f":information: Banded spectral responsivity input :\n{spectrally_resolved_responsivity}",
            alt=f":information: [bold][magenta]Banded[/magenta] spectral responsivity input[/bold]: {spectrally_resolved_responsivity}",
        )
        import pandas.api.types as ptypes

        if ptypes.is_numeric_dtype(spectrally_resolved_responsivity.index):
            spectrally_resolved_responsivity.index.name = "Wavelength"
            spectrally_resolved_responsivity.reset_index().set_index("Wavelength")
        else:
            spectrally_resolved_responsivity.index.name = "Type"
            spectrally_resolved_responsivity.reset_index().set_index("Type")

        spectrally_resolved_responsivity_xarray = (
            spectrally_resolved_responsivity.T.to_xarray()
        )  # Why Transpose ?

    else:
        logger.warning(
            f"You may want to integrate the spectral responsivity input to match the spectral bands of the solar irradiance data !.  Chekout the `--integrate-responsivity` option.",
            alt=f"[bold]You may want to [yellow]integrate[/yellow] the [green]spectral responsivity[/green] input to match the spectral bands of the solar irradiance data ![/bold].  Chekout the `--integrate-responsivity` option.",
        )

        # we need to "return" something, however !
        # hence, to avoid duplication of return stratements
        spectrally_resolved_responsivity_xarray = (
            spectral_responsivity_input.T.to_xarray()
        )  # Why Transpose ?

    logger.debug(
        f"Spectral responsivity input data transformed to an Xarray DataArray :\n{spectral_responsivity_input.T.to_xarray()}",
        alt=f"[green]Spectral responsivity[/green] input data [bold]transformed[/bold] to an Xarray DataArray :\n{spectral_responsivity_input.T.to_xarray()}",
    )

    return spectrally_resolved_responsivity_xarray  # an Xarray


typer_argument_spectral_responsivity = typer.Argument(
    help=spectral_responsivity_typer_help,
    rich_help_panel=rich_help_panel_spectral_responsivity,
    parser=parse_spectral_responsivity,
    show_default=False,
)
typer_argument_spectral_responsivity_pandas = typer.Argument(
    help=spectral_responsivity_typer_help,
    rich_help_panel=rich_help_panel_spectral_responsivity,
    parser=parse_spectral_responsivity,
    callback=callback_spectral_responsivity_pandas,
    show_default=False,
)
typer_option_spectral_responsivity_pandas = typer.Option(
    help=spectral_responsivity_typer_help,
    rich_help_panel=rich_help_panel_spectral_responsivity,
    parser=parse_spectral_responsivity,
    callback=callback_spectral_responsivity_pandas,
    show_default=False,
)
typer_option_integrate_spectral_responsivity = typer.Option(
    help="Integrate the spectral responsivity over Kato bands",
    is_eager=True,
    rich_help_panel=rich_help_panel_spectral_responsivity,
    show_default=True,
)
typer_option_responsivity_column_name = typer.Option(
    help="Column name for responsivity values in `responsivity` CSV input",
    rich_help_panel=rich_help_panel_spectral_responsivity,
    show_default=False,
)
typer_option_wavelength_column_name = typer.Option(
    help="Column name for wavelength values in `wavelength` CSV input",
    # rich_help_panel=rich_help_panel_spectral_responsivity,
    rich_help_panel=rich_help_panel_time_series_data_selection,
    show_default=False,
)

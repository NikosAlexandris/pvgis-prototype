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
from pvgisprototype.api.spectrum.models import PhotovoltaicModuleSpectralResponsivityModel
from pvgisprototype import SpectralFactorSeries, SpectralResponsivity
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_spectral_responsivity,
)


spectral_responsivity_typer_help = "Spectral responsivity of a photovoltaic device expressed in units A/W (amperes per watt) is the electrical current (in amperes) per unit of incident optical power (in watts) at specific wavelengths (CSV string or file, examples: 'path_to_file.csv' or '400,0.3; 500,0.5; 600,0.2')"


# PhotovoltaicModuleType

photovoltaic_module_type_typer_help="Photovoltaic module type for the spectral responsivity. [yellow]Column names in CSV input [bold]must match[/bold] this option's listed types![/yellow]"
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
        spectral_responsivity_series = Series(
            spectral_responsivity_input,
            # name=responsivity_label,
            name=PhotovoltaicModuleSpectralResponsivityModel.cSi,
        )
        spectral_responsivity_series.index.name = wavelength_series_index_name,
        return spectral_responsivity_series

    elif isinstance(spectral_responsivity_input, str) and Path(spectral_responsivity_input).exists():
        spectral_responsivity = read_csv(
                filepath_or_buffer=spectral_responsivity_input,
                index_col=0,
                )
        # Check if required columns are present
        required_index = 'Wavelength [nm]'
        if not required_index == spectral_responsivity.index.name:
            raise ValueError(f"CSV file must contain the column: {required_index}")

        return spectral_responsivity

    elif isinstance(spectral_responsivity_input, str):
        # Parse string input
        try:
            pairs = spectral_responsivity_input.split(';')
            wavelengths = []
            responsivities = []
            for pair in pairs:
                wavelength, responsivity = map(float, pair.split(','))
                wavelengths.append(wavelength)
                responsivities.append(responsivity)
            wavelengths = np.array(wavelengths)
            responsivities = np.array(responsivities)
            spectral_responsivity = Series(responsivities).set_index(wavelengths)

        except ValueError as e:
            raise ValueError("The `responsivity` input string must be in the format 'wavelength1,responsivity1; wavelength2,responsivity2; ...'") from e

    else:
        raise TypeError("Input for responsivity must be either a Path to or a properly formatted CSV string.")

    # return SpectralResponsivity(
    #         value=responsivities,
    #         wavelengths=wavelengths,
    #         )
    return spectral_responsivity


def resolve_spectral_responsivity(
        ):
    """
    """
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
    spectral_responsivity_input : Union[str, Path]
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
    photovoltaic_module_type = list(ctx.params.get('photovoltaic_module_type'))
    # print(f'Parameters : {ctx.params}')
    # print(f'Module type : {type(photovoltaic_module_type)}')
    # print(f'Module type : {photovoltaic_module_type}')
    from pvgisprototype.api.position.models import select_models
    photovoltaic_module_types = select_models(
        PhotovoltaicModuleSpectralResponsivityModel, photovoltaic_module_type
    )  # Using a callback fails!
    # print(f'Module type : {type(photovoltaic_module_types)}')
    # print(f'Module type : {photovoltaic_module_types}')

    if isinstance(spectral_responsivity_input, DataFrame):
        # print(f'Spectral responsivity input type : {type(spectral_responsivity_input)}')
        # print(f'Spectral responsivity input : {spectral_responsivity_input}')
        # if photovoltaic_module_types and photovoltaic_module_types in spectral_responsivity_input.columns:
        if photovoltaic_module_types and all(
            module in spectral_responsivity_input.columns
            for module in photovoltaic_module_types
        ):
            spectral_responsivity_input = spectral_responsivity_input[photovoltaic_module_types]
            # print(f'Spectral responsivity for {photovoltaic_module_types} type : {type(spectral_responsivity_input)}')
            # print(f'Spectral responsivity for {photovoltaic_module_types} : {spectral_responsivity_input}')

        elif not photovoltaic_module_types or photovoltaic_module_types == [PhotovoltaicModuleSpectralResponsivityModel.cSi]:
            spectral_responsivity_input = spectral_responsivity_input[PhotovoltaicModuleSpectralResponsivityModel.cSi]

        else:
            raise KeyError(f"Module type '{photovoltaic_module_types}' not found in spectral responsivity data.")
    
    elif isinstance(spectral_responsivity_input, Series):
        if photovoltaic_module_types and photovoltaic_module_types != [PhotovoltaicModuleSpectralResponsivityModel.cSi]:
            raise KeyError(f"Module type '{photovoltaic_module_types}' not applicable. Input data is already a Series.")
    
    else:
        raise TypeError("Input for responsivity must be either a DataFrame or Series.")

    min_wavelength = float(ctx.params.get("min_wavelength"))
    max_wavelength = float(ctx.params.get("max_wavelength"))
    adjusted_bands = adjust_band_limits(
        DataFrame(KATO_BANDS),
        min_wavelength=min_wavelength,
        max_wavelength=max_wavelength,
    )

    # How to check if not banded ?

    if ctx.params.get("integrate_responsivity"):

        logger.info(
            ":information: [bold][magenta]Banding[/magenta] spectral responsivity input : {spectral_responsivity_input}[/bold]"
        )
        spectrally_resolved_responsivity = generate_banded_data(
            reference_bands=adjusted_bands,
            spectral_data=DataFrame(
                spectral_responsivity_input
            ).T,  # DataFrame Required !
            data_type=RESPONSIVITY_SPECTRAL_DATA,
        )
        logger.info(
            ":information: [bold][magenta]Banded/magenta] spectral responsivity input : {spectrally_resolved_responsivity}[/bold]"
        )
        # return spectrally_resolved_responsivity.T.iloc[:, 0]  # 1 column possible !
        return spectrally_resolved_responsivity.T  # 1 column possible !
    else:
        logger.warning(
            "[bold]You may want to [yellow]integrate[/yellow] the spectral responsivity input to match the spectral bands of the solar irradiance data ![/bold].  Chekout the `--integrate-reference-spectrum` option."
        )

    # Return however a Series !
    # return spectrally_resolved_responsivity.T#[module_type]#.iloc[:,0]  # 1 column possible !
    return DataFrame(spectral_responsivity_input).T  # 1 column possible !


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
    rich_help_panel=rich_help_panel_spectral_responsivity,
    show_default=True,
)
typer_option_responsivity_column_name = typer.Option(
    help='Column name for responsivity values in `responsivity` CSV input',
    rich_help_panel=rich_help_panel_spectral_responsivity,
    show_default=False,
)
typer_option_wavelength_column_name = typer.Option(
    help='Column name for wavelength values in `wavelength` CSV input',
    rich_help_panel=rich_help_panel_spectral_responsivity,
    show_default=False,
)

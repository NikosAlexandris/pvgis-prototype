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
Solar irradiance reference spectrum AM 1.5G
"""

from pvgisprototype.cli.messages import NOT_COMPLETE_CLI
from pvgisprototype.log import logger
import typer
from pandas import to_numeric, DataFrame, read_csv, Series
from pathlib import Path
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_spectrum,
)
from pvgisprototype.api.irradiance.kato_bands import KATO_BANDS
from pvgisprototype.api.spectrum.helpers_pelland import (
    adjust_band_limits,
    generate_banded_data,
)


def parse_reference_spectrum(
    reference_spectrum: str | None,
) -> Series:
    """ """
    if isinstance(reference_spectrum, (str, Path)):
        path = Path(reference_spectrum)
        if path.exists():
            return path
    return reference_spectrum


def callback_reference_spectrum(
    ctx: typer.Context,
    reference_spectrum: Path | str | None,
) -> DataFrame | None:
    """
    Resolve the `reference_spectrum` on a given set of spectral bands.

    The def
    Adjust the Kato bands according to the wavelength range
    """
    if isinstance(reference_spectrum, (str, Path)) and reference_spectrum.exists():
        logger.debug(
            f":information: Reading user-defined reference spectrum {reference_spectrum}!",
            alt=f":information: [bold]Reading user-defined [magenta]reference spectrum ![/magenta][/bold]",
        )
        reference_spectrum = DataFrame(read_csv(Path(reference_spectrum), index_col=0))
        reference_spectrum = reference_spectrum.T
        reference_spectrum.index = to_numeric(reference_spectrum.index, errors="coerce")
        reference_spectrum = reference_spectrum.dropna(axis=0).astype(float)
        reference_spectrum = reference_spectrum.squeeze()
        logger.debug(
            f":information: Parsed user-defined reference spectrum :\n{reference_spectrum}!",
            alt=f":information: Parsed [bold]user-defined [magenta]reference spectrum[/magenta][/bold] :\n{reference_spectrum}",
        )

        return reference_spectrum

    if reference_spectrum is None:
        logger.warning(
            f"No user-requested reference spectrum ! Using the AM 1.5G standard solar spectrum",
            alt=f"[bold][red]No user-requested reference spectrum ![/red] Using the AM 1.5G standard solar spectrum[/bold]",
        )
        from pvlib.spectrum import get_reference_spectra

        # reference_spectrum = DataFrame(get_reference_spectra()['global']).T
        reference_spectrum = get_reference_spectra()["global"]
        # reference_spectrum.index = to_numeric(reference_spectrum.index, errors='coerce')
        # reference_spectrum = reference_spectrum.dropna().astype(float)

        min_wavelength = float(ctx.params.get("min_wavelength"))
        max_wavelength = float(ctx.params.get("max_wavelength"))
        adjusted_bands = adjust_band_limits(
            DataFrame(KATO_BANDS),
            min_wavelength=min_wavelength,
            max_wavelength=max_wavelength,
        )
        reference_spectrum.attrs["long_name"] = "Global Reference Spectrum"
        reference_spectrum.attrs["units"] = "W/m^2"
        reference_spectrum.attrs["description"] = (
            "Standard AM1.5G solar spectrum used for photovoltaic performance analysis."
        )
        reference_spectrum.attrs["source"] = (
            "PVGIS data processing team, based on standardized spectra."
        )

        # How to check if not banded ?

        integrate_reference_spectrum = ctx.params.get("integrate_reference_spectrum")
        if integrate_reference_spectrum:
            # 'resolve' the reference_spectrum
            logger.debug(
                f":information: Banding reference spectrum : {reference_spectrum}",
                alt=f":information: [bold][magenta]Banding[/magenta] reference spectrum : {reference_spectrum}[/bold]",
            )
            spectrally_resolved_reference_spectrum = generate_banded_data(
                reference_bands=adjusted_bands,
                spectral_data=DataFrame(reference_spectrum).T,  # DataFrame required !
                data_type="spectrum",
            )
            logger.debug(
                f":information: Callback function returns the banded reference spectrum :\n{spectrally_resolved_reference_spectrum}",
                alt=f":information: Callback function returns the [bold][magenta]banded[/magenta] reference spectrum : {spectrally_resolved_reference_spectrum}[/bold]",
            )
            return DataFrame(spectrally_resolved_reference_spectrum)

        # --------------------------------------------------------- Review & FixMe
        else:
            return DataFrame(reference_spectrum)

        # reference_spectrum_x = reference_spectrum.T.drop(index='global', errors='ignore')
        # reference_wavelengths = reference_spectrum_x.index.astype(float)

        # kato_band_limits = DataFrame(KATO_BANDS)['Lower limit [nm]'].astype(float)
        # kato_band_limits_set = set(kato_band_limits)

        # if set(reference_wavelengths).issubset(kato_band_limits_set):
        #     logger.debug(
        #             f"All wavelengths in the input reference spectrum are within the Kato band limits : {wavelengths}",
        #             alt=f"[green]All wavelengths in the input reference spectrum are within the Kato band limits[/green] : {wavelengths}",
        #             )
        #     return reference_spectrum
        # else:
        #     message = "Some wavelengths in the reference spectrum are outside the Kato band limits!"
        #     raise ValueError(message)
    # --------------------------------------------------------- Review & FixMe

    # print(f'Resolved reference spectrum ? : {spectrally_resolved_reference_spectrum}')
    # return spectrally_resolved_reference_spectrum


reference_solar_irradiance_spectrum_typer_help = f"The reference spectrum to use for the mismatch calculation. User-defined input {NOT_COMPLETE_CLI} The default is the ASTM G173-03 global tilted spectrum. [(W/m^2)/nm]"

typer_option_reference_spectrum = typer.Option(
    help=reference_solar_irradiance_spectrum_typer_help,
    rich_help_panel=rich_help_panel_spectrum,
    parser=parse_reference_spectrum,
    callback=callback_reference_spectrum,
    show_default=True,
)
typer_option_integrate_reference_spectrum = typer.Option(
    help="Integrate the reference spectrum over Kato bands",
    rich_help_panel=rich_help_panel_spectrum,
    show_default=True,
)

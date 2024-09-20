from pvgisprototype.api.irradiance.kato_bands import KATO_BANDS
from pvgisprototype.log import logger
from xarray import DataArray
from numpy import nan_to_num, concatenate, array, clip, intersect1d, inf
from pandas import DataFrame
import matplotlib.pyplot as plt
from scipy.integrate import simpson


def is_kato_banded(spectral_data: DataArray, wavelengths: str) -> bool:
    """
    Check if the irradiance data is Kato-banded based on the center wavelengths.

    Parameters
    ----------
    irradiance : xarray.DataArray
        Irradiance data with a `center_wavelength` coordinate.

    Returns
    -------
    bool
        True if the irradiance data appears to be Kato-banded, False otherwise.
    """
    from numpy import allclose
    kato_bands_center_wavelengths = list(KATO_BANDS['Center [nm]'].values())
    if spectral_data.coords[wavelengths].size == len(
        kato_bands_center_wavelengths
    ) and allclose(
        spectral_data.coords[wavelengths], kato_bands_center_wavelengths, atol=10
    ):
        return True

    return False


def calculate_spectral_mismatch_factor_mihaylow(
    irradiance,
    responsivity,
    reference_spectrum,
):
    """ """

    # Preparatory steps --- Push Me Upstream ?

    ## Prepare Reference Spectrum

    reference_spectrum = reference_spectrum.to_xarray()
    logger.info(
        f'Reference spectrum input :\n{reference_spectrum}',
        alt=f'[bold]Reference spectrum input[/bold] :\n{reference_spectrum}'
    )

    ## Prepare Responsivity

    # Push me upstream ? -----------------------------------------------------
    if 'Center [nm]' in responsivity.coords:
        responsivity = responsivity.rename({'Center [nm]': 'wavelength'})
    else:
        responsivity = responsivity.rename({'Wavelength': 'wavelength'})

    logger.info(
        f'Responsivity input :\n{responsivity}',
        alt=f'[bold]Responsivity[/bold] input :\n{responsivity}',
    )
    # ------------------------------------------------------------------------

    ## Restrict interpolation to common range
    common_wavelengths = intersect1d(
        irradiance.center_wavelength.values,
        intersect1d(responsivity.wavelength,
                          reference_spectrum.wavelength),
    )
    logger.info(
            f"Intersection of wavelengths across input data : {common_wavelengths}"
            )

    responsivity = responsivity.sel(wavelength=common_wavelengths)
    reference_spectrum = reference_spectrum.sel(wavelength=common_wavelengths)
    irradiance = irradiance.sel(center_wavelength=common_wavelengths)
    logger.info(
        f"Input data limited to common wavelengths:"
        f"Responsivity :\n{responsivity}"
        f"Reference spectrum :\n{reference_spectrum}"
        f"Irradiance :\n{irradiance}"
    )

    # Responsivity -----------------------------------------------------------


    if not is_kato_banded(
            spectral_data=responsivity,
            wavelengths='wavelength',
            ):
        logger.warning(
                f'Responsivity is not Kato-banded !',
                alt=f'[bold yellow]Responsivity is not Kato-banded ![/bold yellow]'
                )
        ## Interpolate Responsivity to Reference Spectrum
        from scipy.interpolate import pchip_interpolate
        responsivity = pchip_interpolate(
            xi=responsivity.wavelength,
            yi=responsivity,
            x=common_wavelengths,
        )
        # responsivity = nan_to_num(responsivity)
        responsivity = clip(responsivity, 0, inf)
        logger.info(
                f"Interpolated responsivity :\n{responsivity}",
                alt=f"[yellow]Interpolated[/yellow] responsivity :\n{responsivity}",
                )

    # Reference Spectrum -----------------------------------------------------

    # Total Reference Spectrum
    total_reference_spectrum = simpson(
        y=reference_spectrum['global'],
        # x=reference_spectrum.wavelength
        x=common_wavelengths
    )
    logger.info(
        f"Total Reference Spectrum :\n{total_reference_spectrum}",
        alt=f"[bold]Total Reference Spectrum[/bold] :\n{total_reference_spectrum}"
    )

    # Useful Reference Spectrum
    effective_reference_spectrum = reference_spectrum * responsivity
    logger.info(
            f"Effective Reference Spectrum :\n{effective_reference_spectrum}",
            alt=f"[bold]Effective Reference Spectrum[/bold] :\n{effective_reference_spectrum}"
            )
    useful_reference_spectrum = simpson(
        y=effective_reference_spectrum['global'],
        # x=reference_spectrum.wavelength
        x=common_wavelengths
    )
    logger.info(
            f"Useful reference spectrum :\n{useful_reference_spectrum}",
            alt=f"[bold][yellow]Useful[/yellow] reference spectrum[/bold] :\n{useful_reference_spectrum}"
            )

    # Observed Irradiance ----------------------------------------------------

    # Interpolate Observed Irradiance to Reference Spectrum
    if is_kato_banded(
        spectral_data=irradiance, wavelengths='center_wavelength'
    ):
        irradiance = irradiance.interp(
            # center_wavelength=reference_spectrum.wavelength,  # target
            center_wavelength=common_wavelengths,  # target
            method="linear",
        )
        logger.info(
                f"Interpolated iradiance :\n{irradiance}",
                alt=f"[bold][yellow]Interpolated[/yellow] irradiance[/bold] :\n{irradiance}",
                )

    # Total Observed Irradiance
    total_observed_irradiance = simpson(
        y=irradiance,
        # x=reference_spectrum.wavelength
        x=common_wavelengths
    )
    logger.info(
            f"Total Observed Irradiance :\n{total_observed_irradiance}",
            alt=f"[bold]Total Observed Irradiance[/bold] :\n{total_observed_irradiance}"
            )

    # Useful Observed Irradiance
    effective_observed_irradiance = irradiance * responsivity
    logger.info(
            f"Effective Observed Irradiance :\n{effective_reference_spectrum}",
            alt=f"[bold]Effective Observed Irradiance[/bold] :\n{effective_reference_spectrum}"
            )
    useful_observed_irradiance = simpson(
        y=effective_observed_irradiance,
        # x=reference_spectrum.wavelength
        x=common_wavelengths
    )
    logger.info(
            f"Useful observed irradiance: {useful_observed_irradiance}",
            alt=f"[bold][yellow]Useful[/yellow] observed irradiance[/bold] :\n{useful_observed_irradiance}"
            )

    # Spectral Mismatch Factor

    a = useful_observed_irradiance / useful_reference_spectrum
    b = total_reference_spectrum / total_observed_irradiance
    spectral_mismatch_factor = a * b

    return spectral_mismatch_factor

from pvgisprototype.api.irradiance.kato_bands import KATO_BANDS
from pvgisprototype.log import logger
from xarray import DataArray
from numpy import nan_to_num, concatenate, array
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

    from devtools import debug
    debug(locals())

    kato_bands_center_wavelengths = list(KATO_BANDS['Center [nm]'].values())
    if spectral_data.coords[wavelengths].size == len(
        kato_bands_center_wavelengths
    ) and allclose(
        spectral_data.coords[wavelengths], kato_bands_center_wavelengths, atol=10
    ):
        return True

    return False


def integrate_reference_spectrum(reference_spectrum, kato_wavelengths):
    """
    Vectorized integration of reference spectrum over Kato bands.
    
    Parameters
    ----------
    reference_spectrum : xarray.DataArray
        The reference spectrum as a DataArray with wavelength and global irradiance values.
    kato_wavelengths : np.ndarray
        Array of Kato center wavelengths.

    Returns
    -------
    integrated_spectrum : np.ndarray
        Reference spectrum integrated over Kato bands.
    """
    # Calculate band edges from center wavelengths
    band_edges = (kato_wavelengths[:-1] + kato_wavelengths[1:]) / 2.0
    band_edges = concatenate([[kato_wavelengths[0] - (band_edges[0] - kato_wavelengths[0])], band_edges])
    band_edges = concatenate([band_edges, [kato_wavelengths[-1] + (kato_wavelengths[-1] - band_edges[-1])]])

    # Extract wavelength and irradiance values
    wavelengths = reference_spectrum.wavelength.values
    irradiance_values = reference_spectrum.values

    # Vectorized integration over each band
    integrated_spectrum = array([
        simpson(
            y=irradiance_values[(wavelengths >= lower_edge) & (wavelengths <= upper_edge)],
            x=wavelengths[(wavelengths >= lower_edge) & (wavelengths <= upper_edge)]
        ) if len(irradiance_values[(wavelengths >= lower_edge) & (wavelengths <= upper_edge)]) > 0 else 0
        for lower_edge, upper_edge in zip(band_edges[:-1], band_edges[1:])
    ])

    return integrated_spectrum


def calculate_spectral_mismatch_factor_mihaylow(
    irradiance,
    responsivity,
    reference_spectrum,
):
    """ """
    reference_spectrum = reference_spectrum.to_xarray()
    logger.info(
        f'`reference_spectrum` input :\n{reference_spectrum}'
    )
    logger.info(
        f'`reference_spectrum` wavelengths :\n{reference_spectrum.wavelength}'
    )

    # Prepare Responsivity ---------------------------------------------------

    logger.info(
        f'`responsivity` input :\n{responsivity}',
    )

    # Push me upstream ? -----------------------------------------------------
    if 'Center [nm]' in responsivity.coords:
        responsivity = responsivity.rename({'Center [nm]': 'wavelength'})
    else:
        responsivity = responsivity.rename({'Wavelength': 'wavelength'})

    logger.info(
        f'Wavelengths in `responsivity` input : {responsivity.wavelength}',
    )
    # ------------------------------------------------------------------------

    # Interpolate Responsivity to Reference Spectrum
    if not is_kato_banded(
            spectral_data=responsivity,
            wavelengths='wavelength',
            ):

        logger.warning(
                f'Responsivity is not Kato-banded !',
                )

        from scipy.interpolate import pchip_interpolate
        responsivity = pchip_interpolate(
            xi=responsivity.wavelength,
            yi=responsivity,
            x=reference_spectrum.wavelength,
        )
        responsivity = nan_to_num(responsivity)

        logger.info(
                f"Interpolated responsivity :\n{responsivity}",
                alt=f"[yellow]Interpolated[/yellow] responsivity :\n{responsivity}",
                )
    # Reference Spectrum -----------------------------------------------------

    # Total Reference Spectrum
    total_reference_spectrum = simpson(
        y=reference_spectrum['global'], x=reference_spectrum.wavelength
    )

    # Useful Reference Spectrum
    effective_reference_spectrum = reference_spectrum * responsivity
    useful_reference_spectrum = simpson(
        y=effective_reference_spectrum['global'],
        x=reference_spectrum.wavelength,
    )

    # Observed Irradiance ----------------------------------------------------

    logger.info(
            f'`irradiance` input :\n{irradiance}'
            )

    # Interpolate Observed Irradiance to Reference Spectrum
    if is_kato_banded(
        spectral_data=irradiance, wavelengths='center_wavelength'
    ):
        irradiance = irradiance.interp(
            center_wavelength=reference_spectrum.wavelength,  # target
            method="linear",
        )
        print()
        print(f"Irradiance : {irradiance}")
        print()
    logger.info(
            f"Interpolated iradiance :\n{irradiance}",
            alt=f"[yellow]Interpolated[/yellow] irradiance :\n{irradiance}",
            )

    # Total Observed Irradiance
    total_observed_irradiance = simpson(
        y=irradiance,
        x=reference_spectrum.wavelength,
    )

    # Useful Observed Irradiance
    effective_observed_irradiance = irradiance * responsivity
    useful_observed_irradiance = simpson(
        y=effective_observed_irradiance,
        x=reference_spectrum.wavelength,
    )

    logger.info(f"Total reference spectrum: {total_reference_spectrum}")
    logger.info(f"Useful reference spectrum: {useful_reference_spectrum}")
    logger.info(f"Total observed irradiance: {total_observed_irradiance}")
    logger.info(f"Useful observed irradiance: {useful_observed_irradiance}")

    # Spectral Mismatch Factor

    a = useful_observed_irradiance / useful_reference_spectrum
    b = total_reference_spectrum / total_observed_irradiance
    spectral_mismatch_factor = a * b

    return spectral_mismatch_factor

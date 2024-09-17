from pandas import DataFrame
from xarray import DataArray
from pvgisprototype.log import log_function_call, logger


# def calculate_spectral_mismatch(
#     irradiance: DataFrame,
#     responsivity: DataFrame,
#     reference_spectrum: DataFrame,
# ):
#     """ """
#     print(f"Irradiance : {irradiance}")
#     print(f"Responsivity : {responsivity}")

#     if irradiance.index.equals(
#         responsivity.T.index
#     ) and irradiance.index.equals(reference_spectrum.index):
#         print(f"Irradiance : {irradiance}")
#         print(f"Responsivity : {responsivity}")

#         uf_reference = (
#             responsivity.T * reference_spectrum.T
#         ).sum() / reference_spectrum.T.sum()
#         print(f"Useful reference spectrum fraction : {uf_reference}")

#         uf_irradiance = (responsivity.T * irradiance.T).T.sum() / irradiance.sum()
#         print(f"Useful spectrum fraction : {uf_irradiance}")

#         return uf_irradiance / uf_reference


@log_function_call
def calculate_spectral_mismatch_pelland(
    irradiance: DataArray,
    responsivity: DataFrame,
    reference_spectrum: DataFrame,
) -> DataFrame:
    """Calculate the spectral mismatch factor for each PV technology based on
    Pelland 2022.

    Notes
    -----
    Some Python source code shared via personal communication.

    """
    # Verify the reference spectrum is valid (no zero or near-zero values) ?
    print(f'Reference spectrum : {type(reference_spectrum)}')
    print(f'Reference spectrum : {reference_spectrum}')
    # if (reference_spectrum <= 0).any():
    #     raise ValueError(
    #         "The reference spectrum contains zero or negative values, which are invalid."
    #     )
    # else:
    #     print(f'Reference spectrum input : {reference_spectrum}')

    # Align wavelengths (columns) between dataframes
    # if not isinstance(irradiance, DataFrame):
    #     irradiance = irradiance.to_dataframe()
    # wavelengths = irradiance.columns.intersection(responsivity.index).intersection(
    #     reference_spectrum.columns
    # )
    import numpy
    logger.info(
            f'Wavelengths in `irradiance` input : {irradiance.center_wavelength.values}',
            )
    
    # Push me upstream !
    if 'Center [nm]' in responsivity.coords:
        responsivity = responsivity.rename({'Center [nm]': 'center_wavelength'})
    else:
        responsivity = responsivity.rename({'Wavelength': 'center_wavelength'})
    # ------------------------------------------------------------------------

    logger.info(
            f'Wavelengths in `responsivity` input : {responsivity}',
            )
    logger.info(
            f'Wavelengths in `reference_spectrum` input : {reference_spectrum.columns}'
            )
    common_wavelengths = numpy.intersect1d(
        irradiance.center_wavelength.values,
        numpy.intersect1d(responsivity.center_wavelength, reference_spectrum.columns),
    )
    logger.info(
            f"Intersection of wavelengths across input data : {common_wavelengths}"
            )

    # useful reference spectrum (average over the reference spectrum)
    responsivity_selected = responsivity.sel(center_wavelength=common_wavelengths)
    logger.info(
            f"Selected responsivity data : {responsivity_selected}"
            )

    reference_spectrum_selected = reference_spectrum.loc["global", common_wavelengths]
    logger.info(
            f"Selected reference spectrum data : {reference_spectrum_selected}"
            )

    useful_reference = (
        responsivity_selected * reference_spectrum_selected
    ).sum() / reference_spectrum_selected.sum()
    logger.info(
        f"Useful fraction of reference spectrum : {useful_reference}"
    )

    # useful irradiance (time-varying)
    irradiance_selected = irradiance.sel(center_wavelength=common_wavelengths)
    logger.info(
        f"Selected irradiance data : {irradiance_selected}"
    )
    sum_of_responsivity_by_irradiance = (
        responsivity_selected * irradiance_selected
    ).sum(dim="center_wavelength")
    logger.info(
            f"Sum of responsivity * irradiance : {sum_of_responsivity_by_irradiance}"
            )
    sum_of_irradiance = (
        irradiance_selected
    ).sum(dim="center_wavelength")
    logger.info(
            f"Sum of irradiance : {sum_of_irradiance}"
            )

    useful_irradiance = (
        responsivity_selected * irradiance_selected
    ).sum(dim="center_wavelength") / irradiance_selected.sum(dim='center_wavelength')
    logger.info(
        f"Useful fraction of irradiance : {useful_irradiance}"
    )

    spectral_mismatch = useful_irradiance / useful_reference

    logger.info(
            f"Spectral mismatch = {spectral_mismatch}"
            )
    return spectral_mismatch.to_numpy()

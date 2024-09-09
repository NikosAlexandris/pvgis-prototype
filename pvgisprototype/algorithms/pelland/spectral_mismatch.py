from pandas import DataFrame


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


def calculate_spectral_mismatch_pelland(
    irradiance: DataFrame,
    responsivity: DataFrame,
    reference_spectrum: DataFrame,
) -> DataFrame:
    """Calculate the spectral mismatch factor for each PV technology based on
    Pelland 2022.

    Notes
    -----
    Some Python source code shared via personal communication.

    """
    # print(f'Irradiance input : {irradiance}')
    # print(f'Responsivity input : {responsivity}')

    # Verify the reference spectrum is valid (no zero or near-zero values) ?
    if (reference_spectrum <= 0).any().any():
        raise ValueError(
            "The reference spectrum contains zero or negative values, which are invalid."
        )
    # else:
    #     print(f'Reference spectrum input : {reference_spectrum}')

    # Align wavelengths (columns) between dataframes
    wavelengths = irradiance.columns.intersection(responsivity.index).intersection(
        reference_spectrum.columns
    )

    # useful reference spectrum (average over the reference spectrum)
    useful_reference = (
        responsivity.loc[wavelengths]
        .mul(reference_spectrum.loc["global", wavelengths])
        .sum()
        / reference_spectrum.loc["global", wavelengths].sum()
    )

    # useful irradiance (time-varying)
    useful_irradiance = responsivity.loc[wavelengths].mul(irradiance[wavelengths]).sum(
        axis=1
    ) / irradiance[wavelengths].sum(axis=1)

    spectral_mismatch = useful_irradiance / useful_reference

    # return DataFrame(spectral_mismatch, index=irradiance.index, columns=["Spectral Mismatch"])
    return spectral_mismatch.to_numpy()

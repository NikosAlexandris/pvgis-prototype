from numpy import concatenate, unique, nan_to_num, isnan
from scipy.interpolate import pchip_interpolate


def interpolate_spectral_data(
    data,
    reference_wavelengths,
    data_name: str,
):
    """Interpolate spectral data to a set of higher spectral resolution wavelengths.

    In overview, this function adds and fills missing spectral wavelengths
    using the PCHIP interpolation. The function assumes that the input Xarray
    has a dimension / coordinate named `wavelength`.
    
    Parameters
    ----------
    data : xarray.DataArray
        The `data` to interpolate.

    reference_wavelengths : numpy.array
        The reference spectral wavelengths over which to interpolate the input
        `data`.

    Returns
    -------
    xarray.DataArray
        The interpolated spectral data.
    """
    # Add any missing spectral wavelengths and fill missing values with NaN
    all_wavelengths = unique(
        concatenate((data.wavelength, reference_wavelengths))
    )
    data = data.interp(
        wavelength=all_wavelengths,
        method="linear",
    )
    # Mask of missing values
    nan_mask = isnan(data.values)

    if nan_mask.any():
        # get observed xi and yi, define x for which to interpolate
        observed_wavelengths = data.wavelength.values[~nan_mask]
        observed_data = data.values[~nan_mask]
        missing_wavelengths = data.wavelength.values[nan_mask]

        # interpolate missing values
        interpolated_values = pchip_interpolate(
            xi=observed_wavelengths,
            yi=observed_data,
            x=missing_wavelengths,
        )
        interpolated_values = nan_to_num(interpolated_values)

        # fill interpolated values into`data`
        data.values[nan_mask] = interpolated_values

    return data

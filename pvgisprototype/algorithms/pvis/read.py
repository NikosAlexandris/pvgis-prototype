import numpy as np


def read_spectral_response(
    filename: str,
) -> tuple:
    """
    Read spectral response data from a file.

    Parameters
    ----------
    filename : str
        Path to the file containing spectral response data.

    Returns
    -------
    tuple
        A tuple containing:
        - wavelengths: 1D NumPy array of wavelengths.
        - response: 2D NumPy array of spectral response values.
        - STCresponse: Float value of Standard Test Condition response.

    Raises
    ------
    IOError
        If the file cannot be opened or read correctly.
    """
    try:
        with open(filename, "r") as fp:
            STCresponse = float(fp.readline().strip())
            data = np.loadtxt(fp, delimiter=",", ndmin=2)
    except IOError as e:
        raise IOError(
            f"Could not open or read spectral response file: {filename}"
        ) from e

    if data.size == 0:
        return np.array([]), np.array([]), STCresponse

    wavelengths = data[:, 0]
    response = data[:, 1:].T  # Transposing to rearrange spectral responses

    return wavelengths, response, STCresponse

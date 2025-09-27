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
from pandas import concat, Series, to_numeric, DataFrame
from pvgisprototype.constants import DATA_TYPE_DEFAULT
import numpy


def integrate(e):
    # print(f'Input to integrate : {e}')
    # print(f'Indices to integrate over : {e.T.index}')
    return numpy.trapz(e, x=e.T.index, axis=-1)

 
def adjust_band_limits(
    bands: DataFrame,
    min_wavelength: float,
    max_wavelength: float,
    lower_band_wavelength_limit_name: str = "Lower limit [nm]",
    center_band_wavelength_limit_name: str = "Center [nm]",
    upper_band_wavelength_limit_name: str = "Upper limit [nm]",
    dtype: str = DATA_TYPE_DEFAULT,
) -> DataFrame:
    """ """
    # bands = bands.astype(float)
    bands = bands.astype(dtype)
    bands = bands[
        numpy.logical_and(
            min_wavelength < bands[upper_band_wavelength_limit_name],
            max_wavelength > bands[lower_band_wavelength_limit_name],
        )
    ]
    bands.reset_index(inplace=True, drop=True)

    # Adjust the lower limit of the first band using .loc[]
    # bands.iloc[0,:][lower_band_wavelength_limit_name] = max(min_wavelength,bands.iloc[0,:][lower_band_wavelength_limit_name])
    bands.loc[bands.index[0], lower_band_wavelength_limit_name] = max(
        min_wavelength, bands.loc[bands.index[0], lower_band_wavelength_limit_name]
    )

    # Adjust the upper limit of the last band using .loc[]
    # bands.iloc[len(bands)-1,:][upper_band_wavelength_limit_name] = min(max_wavelength,bands.iloc[len(bands)-1,:][upper_band_wavelength_limit_name])
    bands.loc[bands.index[-1], upper_band_wavelength_limit_name] = min(
        max_wavelength, bands.loc[bands.index[-1], upper_band_wavelength_limit_name]
    )

    return bands


def generate_banded_data(
    reference_bands,
    spectral_data,
    data_type,
    lower_band_wavelength_limit_name: str = 'Lower limit [nm]',
    center_band_wavelength_name: str = 'Center [nm]',
    upper_band_wavelength_limit_name: str = 'Upper limit [nm]',
    dtype: str = DATA_TYPE_DEFAULT,
):
    """
    """
    # Make a copy of original data to keep it unmodified
    data = spectral_data.copy()

    # Add missing reference band edges in the data
    for band_edge in reference_bands[lower_band_wavelength_limit_name].tolist() + [
        reference_bands[upper_band_wavelength_limit_name].iloc[-1]
    ]:
        if band_edge not in data.columns:
            closest_smaller_edge = max(
                [column for column in data.columns if column < band_edge]
            )
            # Insert new edge after the closest smaller one
            data.insert(
                data.columns.get_loc(closest_smaller_edge) + 1, band_edge, numpy.nan
            )

    # Now do dataframe interpolation to get the values at the band edges
    data = data.apply(to_numeric)
    data.interpolate(method="values", axis=1, inplace=True)

    # Do numerical integration (trapezoidal) to get total for each band
    banded_data = DataFrame(
        data=numpy.nan,
        index=data.index,
        columns=reference_bands[center_band_wavelength_name],
        dtype=dtype,
    )

    # Compute one column at a time
    for col in numpy.arange(0, len(reference_bands)):
        col_list = [
            idx
            for idx in range(len(data.columns))
            if (
                data.columns[idx] >= reference_bands[lower_band_wavelength_limit_name][col]
                and data.columns[idx] <= reference_bands[upper_band_wavelength_limit_name][col]
            )
        ]
        if data_type == "responsivity":
            banded_data[reference_bands[center_band_wavelength_name][col]] = integrate(
                data.iloc[:, col_list]
            ) / (
                reference_bands[upper_band_wavelength_limit_name][col]
                - reference_bands[lower_band_wavelength_limit_name][col]
            )

            # Rename columns !  Ugly Hacks ---------------------------------------
            if (
                banded_data.columns.name == center_band_wavelength_name
                or banded_data.columns.name == "Wavelength"
            ):
                banded_data.columns.name = "center_wavelength"

        elif data_type == "spectrum":
            banded_data[reference_bands[center_band_wavelength_name][col]] = integrate(
                data.iloc[:, col_list]
            )

    return banded_data

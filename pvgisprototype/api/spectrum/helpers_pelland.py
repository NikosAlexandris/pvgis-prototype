from pandas import concat, Series, to_numeric, DataFrame
import numpy


def integrate(e):
    # print(f'Input to integrate : {e}')
    # print(f'Indices to integrate over : {e.T.index}')
    return numpy.trapz(e, x=e.T.index, axis=-1)

 
# def adjust_band_limits(bands,wavelengths):
def adjust_band_limits(
    bands: DataFrame,
    min_wavelength: float,
    max_wavelength: float,
) -> DataFrame:
    """
    """
    bands=bands.astype(float)
    bands = bands[numpy.logical_and(min_wavelength<bands['Upper limit [nm]'],max_wavelength>bands['Lower limit [nm]'])]
    bands.reset_index(inplace=True,drop=True)

    # Adjust the lower limit of the first band using .loc[]
    # bands.iloc[0,:]['Lower limit [nm]'] = max(min_wavelength,bands.iloc[0,:]['Lower limit [nm]'])
    bands.loc[bands.index[0], 'Lower limit [nm]'] = max(min_wavelength, bands.loc[bands.index[0], 'Lower limit [nm]'])

    # Adjust the upper limit of the last band using .loc[]
    # bands.iloc[len(bands)-1,:]['Upper limit [nm]'] = min(max_wavelength,bands.iloc[len(bands)-1,:]['Upper limit [nm]'])
    bands.loc[bands.index[-1], 'Upper limit [nm]'] = min(max_wavelength, bands.loc[bands.index[-1], 'Upper limit [nm]'])

    return bands


# def generate_banded_data(bands,data_original,data_type):    
#def generate_banded_data(
#    reference_bands,
#    spectral_data,
#    data_type,
#):
#    #Make a copy of original data to keep it unmodified
#    data=spectral_data.copy()
#    #Add in columns with values at the band edges, excluding reference_bands that are out of bounds
#    for band_edge in concat([reference_bands['Lower limit [nm]'], Series(reference_bands['Upper limit [nm]'][len(reference_bands)-1])]):
#        if ~numpy.any(band_edge == data.columns):
#            closest_smaller=max([x for x in data.columns if x<band_edge])
#            data.insert(data.columns.get_loc(closest_smaller)+1,band_edge,numpy.nan)
                
#    #Now do dataframe interpolation to get the values at the band edges
#    data=data.apply(to_numeric)
#    data.interpolate(method='values',axis=1,inplace=True)
    
#    #Do numerical integration (trapezoidal) to get total for each band
#    banded_data=DataFrame(data=numpy.nan,index=data.index,columns=reference_bands['Lower limit [nm]'],dtype='float64')

#    #Compute one column at a time
#    for col in numpy.arange(0,len(reference_bands)):
#        col_list=[idx for idx in range(len(data.columns)) if (data.columns[idx]>=reference_bands['Lower limit [nm]'][col] and data.columns[idx]<=reference_bands['Upper limit [nm]'][col])]
#        if data_type=='responsivity':
#            banded_data[reference_bands['Lower limit [nm]'][col]]=integrate(data.iloc[:,col_list])/(reference_bands['Upper limit [nm]'][col]-reference_bands['Lower limit [nm]'][col])
#        elif data_type=='spectrum':
#            banded_data[reference_bands['Lower limit [nm]'][col]]=integrate(data.iloc[:,col_list])

#    return banded_data


def generate_banded_data(
    reference_bands,
    spectral_data,
    data_type,
):
    """
    """
    # Make a copy of original data to keep it unmodified
    data = spectral_data.copy()
    # print(f'Input data : {data}')

    # Add missing reference band edges in the data
    for band_edge in reference_bands["Lower limit [nm]"].tolist() + [reference_bands["Upper limit [nm]"].iloc[-1]]:
        if band_edge not in data.columns:
            closest_smaller_edge = max([column for column in data.columns if column < band_edge])
            # Insert new edge after the closest smaller one
            data.insert(data.columns.get_loc(closest_smaller_edge) + 1, band_edge, numpy.nan)
    # print(f'+ New Spectral Wavelengths : {data}')

    # Now do dataframe interpolation to get the values at the band edges
    data = data.apply(to_numeric)
    data.interpolate(method="values", axis=1, inplace=True)
    # print(f'+ Interpolated new wavelengths : {data}')

    # Do numerical integration (trapezoidal) to get total for each band
    banded_data = DataFrame(
        data=numpy.nan, index=data.index, columns=reference_bands["Center [nm]"], dtype="float64"
    )

    # Compute one column at a time
    for col in numpy.arange(0, len(reference_bands)):
        col_list = [
            idx
            for idx in range(len(data.columns))
            if (
                data.columns[idx] >= reference_bands["Lower limit [nm]"][col]
                and data.columns[idx] <= reference_bands["Upper limit [nm]"][col]
            )
        ]
        if data_type == "responsivity":
            banded_data[reference_bands["Center [nm]"][col]] = integrate(
                data.iloc[:, col_list]
            ) / (reference_bands["Upper limit [nm]"][col] - reference_bands["Lower limit [nm]"][col])
            # print('Banded responsivity :')

        elif data_type == "spectrum":
            banded_data[reference_bands["Center [nm]"][col]] = integrate(
                data.iloc[:, col_list]
            )
            # print('Banded spectrum :')

        # print(f'{banded_data}')

    return banded_data

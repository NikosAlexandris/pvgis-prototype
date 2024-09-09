import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.integrate import simps
import matplotlib.pyplot as plt
import xarray as xr


def calculate_spectral_factor(
    row, AM15G_wavelength, AM15G_irradiance, SR_wavelength, SR_responsivity, plot=False, verbose=False
):
    """
    Calculate the spectral mismatch factor using AM1.5G spectrum and spectral responsivity data.

    Parameters
    ----------
    row : dict-like
        A dictionary-like row of data containing the global radiation values for different intervals.
    AM15G_wavelength : np.ndarray
        Array of wavelengths for the AM1.5G spectrum.
    AM15G_irradiance : np.ndarray
        Array of irradiance values for the AM1.5G spectrum.
    SR_wavelength : np.ndarray
        Array of wavelengths for the spectral responsivity.
    SR_responsivity : np.ndarray
        Array of responsivity values corresponding to the wavelengths.
    plot : bool, optional
        If True, plot the results. Default is False.
    verbose : bool, optional
        If True, print detailed output. Default is False.

    Returns
    -------
    ratio : float
        The calculated spectral mismatch factor.
    """

    # Wavelength intervals in micrometers converted to nanometers
    wavelength_intervals_nm = [
        [240, 272], [272, 283], [283, 307], [307, 328], [328, 363],
        [363, 408], [408, 452], [452, 518], [518, 540], [540, 550],
        [550, 567], [567, 605], [605, 625], [625, 667], [667, 684],
        [684, 704], [704, 743], [743, 791], [791, 844], [844, 889],
        [889, 975], [975, 1046], [1046, 1194], [1194, 1516], [1516, 1613],
        [1613, 1965], [1965, 2153], [2153, 2275], [2275, 3001], [3001, 3635],
        [3635, 3991], [3991, 4606]
    ]
    
    interval_widths_nm = np.array([end - start for start, end in wavelength_intervals_nm])

    # Extract total irradiance data for the current row
    total_irradiance_values = np.array([row[f'global_radiation_kato{i}[w/m2]'] for i in range(1, 33)])

    # Calculate the average irradiance density (W/m^2/nm) for each interval
    average_irradiance_density = total_irradiance_values / interval_widths_nm

    # Create the x-values for the staircase plot (start and end points of each interval)
    wavelengths_x_nm = np.array([val for interval in wavelength_intervals_nm for val in interval] + [wavelength_intervals_nm[-1][1]])

    # Create the y-values for the staircase plot (repeat each density value for the interval)
    irradiance_y_density = np.repeat(average_irradiance_density, 2)
    irradiance_y_density = np.append(irradiance_y_density, 0)  # Add a zero to complete the last step

    # PCHIP interpolation of the SR data to AM1.5G wavelengths
    sr_pchip_interpolator = PchipInterpolator(SR_wavelength, SR_responsivity, extrapolate=False)
    sr_interpolated_am15g = sr_pchip_interpolator(AM15G_wavelength)
    sr_interpolated_am15g = np.nan_to_num(sr_interpolated_am15g)

    # Multiply the interpolated SR values with the corresponding irradiance values
    product_am15g_sr = AM15G_irradiance * sr_interpolated_am15g

    # Integrate the AM1.5G spectrum and the product using the Simpson's rule
    integral_am15g = simps(AM15G_irradiance, AM15G_wavelength)
    integral_am15g_sr = simps(product_am15g_sr, AM15G_wavelength)

    # Interpolate the staircase irradiance data to AM1.5G wavelengths
    staircase_interpolated_am15g = np.interp(
        AM15G_wavelength, wavelengths_x_nm, irradiance_y_density, left=irradiance_y_density[0], right=0
    )

    # Calculate the product of the interpolated staircase irradiance and SR data
    product_staircase_sr = staircase_interpolated_am15g * sr_interpolated_am15g

    # Integrate the interpolated staircase data and the product using the Simpson's rule
    integral_staircase = simps(staircase_interpolated_am15g, AM15G_wavelength)
    integral_staircase_sr = simps(product_staircase_sr, AM15G_wavelength)

    # Calculate the ratio of the integrals scaled by the total irradiance
    ratio = (integral_staircase_sr / integral_am15g_sr) * (integral_am15g / integral_staircase)

    if verbose:
        total_irradiance = np.sum(average_irradiance_density * interval_widths_nm)
        print(f"Calculated total irradiance: {total_irradiance} W/m^2")
        print(f'integral_staircase: {integral_staircase}')
        print(f'integral AM15G: {integral_am15g}')
        print(f'integral_staircase_sr: {integral_staircase_sr}')
        print(f'integral_am15g_sr: {integral_am15g_sr}')
        print(f"The ratio of (staircase irradiance x SR) over (AM1.5G x SR) is: {ratio}")

    if plot:
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Plot AM1.5G spectrum on the primary y-axis
        ax1.plot(AM15G_wavelength, AM15G_irradiance, label='AM1.5G Spectrum', color='red')
        ax1.set_xlabel('Wavelength (nm)')
        ax1.set_ylabel('Irradiance (W/m^2/nm)', color='red')
        ax1.tick_params(axis='y', labelcolor='red')

        # Create a secondary y-axis for the responsivity and staircase data
        ax2 = ax1.twinx()
        ax2.plot(AM15G_wavelength, sr_interpolated_am15g, label='Interpolated SR (PCHIP)', color='green')
        ax2.set_ylabel('Responsivity (A/W) / Staircase Irradiance Density (W/m^2/nm)', color='green')
        ax2.tick_params(axis='y', labelcolor='green')

        # Plot the staircase spectral irradiance data as steps
        ax1.step(wavelengths_x_nm, irradiance_y_density, label='Staircase Irradiance', color='blue', where='post', alpha=0.7)

        # Adding title and grid
        plt.title('AM1.5G Spectrum, Interpolated SR, and Staircase Irradiance (PCHIP)')

        # Show the grid
        ax1.grid(True)

        # Show the legend
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')
        plt.xlim(300, 1300)

        # Display the plot
        plt.show()

    return ratio

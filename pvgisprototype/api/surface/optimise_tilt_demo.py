from scipy.optimize import minimize
import numpy as np


incidence_angle = np.deg2rad(60)  # For example, 60 degrees
max_irradiance = 1  # 100%
attenuation_factor = 0.124


# callback function to print the optimization process
def callback(tilt):
    print(f"Current guess: tilt = {np.rad2deg(tilt)} degrees, Irradiance = {calculate_irradiance(tilt)}")


def calculate_irradiance(tilt):
    return -max_irradiance * np.cos(tilt - incidence_angle) 


# minimize negative irradiance
def irradiance(theta):
    return -max_irradiance * np.exp(-attenuation_factor / np.cos(incidence_angle)) * np.cos(tilt - incidence_angle)


tilt_0 = np.deg2rad(45)
print(f"Initial guess: tilt = {np.rad2deg(tilt_0)} degrees, Irradiance = {calculate_irradiance(tilt_0)}")


optimal_tilt = minimize(calculate_irradiance, tilt_0, method='Nelder-Mead', callback=callback)
print(f"\nOptimal tilt = {np.rad2deg(optimal_tilt.x)} degrees, Irradiance = {calculate_irradiance(optimal_tilt.x)}")

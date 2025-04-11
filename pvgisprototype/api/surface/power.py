from numpy import ndarray
from xarray import DataArray
from pvgisprototype.api.position.models import ShadingModel
from pvgisprototype.api.power.broadband import (
    calculate_photovoltaic_power_output_series,
)
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.surface.parameter_models import SurfacePositionOptimizerMode
from pvgisprototype.constants import (
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    SPECTRAL_FACTOR_DEFAULT,
    TEMPERATURE_DEFAULT,
    WIND_SPEED_DEFAULT,
)
from pvgisprototype import (
    LinkeTurbidityFactor,
    SpectralFactorSeries,
    TemperatureSeries,
    WindSpeedSeries,
)

"""
Create the functions that the optimizer will minimize, in order to find the point where the 
power output/irradiance are maximized.

A function for each case. Is it necessary??? 
    - Maybe I can have just one function (although i think scipy function works differently
     when calling the function if it's one or two variables )
    - Anyway, maybe I could have two functions (for the 1D problem and the 2D problem) 

"""

def calculate_mean_negative_photovoltaic_power_output(
    surface_angle,
    arguments: dict,
    mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
):
    """
    Returns
    -------
    The mean of the negative power output

    """
    if mode == SurfacePositionOptimizerMode.Tilt:
        photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
            surface_tilt=surface_angle,
            **arguments,
        )

    if mode == SurfacePositionOptimizerMode.Orientation:
        photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
            surface_orientation=surface_angle,
            **arguments,
        )

    if mode == SurfacePositionOptimizerMode.Orientation_and_Tilt:
        photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
            surface_orientation=surface_angle[0],
            surface_tilt=surface_angle[1],
            **arguments,
        )

    return -(photovoltaic_power_output_series).value.mean()

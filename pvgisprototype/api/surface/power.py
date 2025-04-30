from numpy import ndarray
from xarray import DataArray
from pvgisprototype.api.position.models import ShadingModel
from pvgisprototype.api.power.broadband import (
    calculate_photovoltaic_power_output_series,
)
from pvgisprototype.algorithms.huld.photovoltaic_module import PhotovoltaicModuleModel
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
    location_parameters: dict,
    global_horizontal_irradiance: ndarray | None = None,
    direct_horizontal_irradiance: ndarray | None = None,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(
        value=SPECTRAL_FACTOR_DEFAULT
    ),
    temperature_series: TemperatureSeries = TemperatureSeries(
        value=TEMPERATURE_DEFAULT
    ),
    wind_speed_series: WindSpeedSeries = WindSpeedSeries(value=WIND_SPEED_DEFAULT),
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(
        value=LINKE_TURBIDITY_TIME_SERIES_DEFAULT
    ),
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
):
    """
    Returns
    -------
    The mean of the negative power output

    """
    common_parameters = {
        "global_horizontal_irradiance": global_horizontal_irradiance,
        "direct_horizontal_irradiance": direct_horizontal_irradiance,
        "spectral_factor_series": spectral_factor_series,
        "temperature_series": temperature_series,
        "wind_speed_series": wind_speed_series,
        "horizon_profile": horizon_profile,
        "shading_model": shading_model,
        "linke_turbidity_factor_series": linke_turbidity_factor_series,
        "photovoltaic_module": photovoltaic_module,
        **location_parameters,
    }

    if mode == SurfacePositionOptimizerMode.Tilt:
        photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
            surface_tilt=surface_angle,
            **common_parameters,
        )

    if mode == SurfacePositionOptimizerMode.Orientation:
        photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
            surface_orientation=surface_angle,
            **common_parameters,
        )

    if mode == SurfacePositionOptimizerMode.Orientation_and_Tilt:
        photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
            surface_orientation=surface_angle[0],
            surface_tilt=surface_angle[1],
            **common_parameters,
        )

    return -(photovoltaic_power_output_series).value.mean()

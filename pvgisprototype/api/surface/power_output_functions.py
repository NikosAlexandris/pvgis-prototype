from pvgisprototype import SurfaceOrientation, SurfaceTilt
from pvgisprototype.api.power.broadband import (
    calculate_photovoltaic_power_output_series,
)

"""
Create the functions that the optimizer will minimize, in order to find the point where the 
power output/irradiance are maximized.

A function for each case. Is it necessary??? 
    - Maybe I can have just one function (although i think scipy function works differently
     when calling the function if it's one or two variables )
    - Anyway, maybe I could have two functions (for the 1D problem and the 2D problem) 

"""


def negative_power_output_for_tilt(
    surface_tilt: float,
    parameters,
):
    return -(
        calculate_photovoltaic_power_output_series(
            surface_tilt=SurfaceTilt(value=surface_tilt, unit="radians"), **parameters
        ).value.mean()
    )


def negative_power_output_for_orientation(
    surface_orientation: float,
    parameters,
):
    return -(
        calculate_photovoltaic_power_output_series(
            surface_orientation=SurfaceOrientation(
                value=surface_orientation, unit="radians"
            ),
            **parameters,
        ).value.mean()
    )


def negative_power_output_for_tilt_orientation(
    surface_parameters,
    parameters,
):
    return -(
        calculate_photovoltaic_power_output_series(
            surface_tilt=SurfaceTilt(value=surface_parameters[0], unit="radians"),
            surface_orientation=SurfaceOrientation(
                value=surface_parameters[1], unit="radians"
            ),
            **parameters,
        ).value.mean()
    )

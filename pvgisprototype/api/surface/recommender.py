from pvgisprototype import (
        Latitude,
        SurfaceOrientation,
        )
from pvgisprototype.api.surface.parameter_models import SurfacePositionOptimizerMode
from math import radians


def recommend_surface_position(
    mode: SurfacePositionOptimizerMode,
    latitude: Latitude,
    recommended_surface_tilt: float,
    recommended_surface_orientation: SurfaceOrientation = SurfaceOrientation(
        value=radians(180), unit="radians"
    ),  # SurfaceOrientation().default_radians
):
    """
    """
    if mode == SurfacePositionOptimizerMode.Tilt:
        # initial guess for surface tilt !
        return recommended_surface_tilt

    if mode == SurfacePositionOptimizerMode.Orientation:
        # initial guess for surface orientation
        if latitude < 0:  # = in southern hemisphere
            return 0
        return recommended_surface_orientation.radians
    
    if mode == SurfacePositionOptimizerMode.Orientation_and_Tilt:
        return [
                recommended_surface_orientation.radians,
                recommended_surface_tilt,
                ]

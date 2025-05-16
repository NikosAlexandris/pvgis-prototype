from pvgisprototype import (
        Latitude,
        SurfaceOrientation,
        )
from pvgisprototype.api.surface.parameter_models import SurfacePositionOptimizerMode
from math import radians


def recommend_surface_position(
    mode: SurfacePositionOptimizerMode,
    latitude: float,
    recommended_surface_tilt: float,
    recommended_surface_orientation: float = radians(180),
):
    """
    Provide an initial guess for the optimisation process based on the provided parameters.

    Parameters
    ----------
    mode: SurfacePositionOptimizerMode
        The mode of the optimisation process.
    latitude: float
        The latitude of the location of interest.
    recommended_surface_tilt: float
        The recommended surface tilt for the optimisation process.
    recommended_surface_orientation: float, optional
        The recommended surface orientation for the optimisation process. Defaults to π.
    
    Returns
    -------
    float or list of floats
        The initial guess for the optimisation process.
    """
    if mode == SurfacePositionOptimizerMode.Tilt:
        # NOTE INITIAL GUESS FOR SURFACE TILT OPTIMISATION
        # NOTE SURFACE TILT IS IN RADIANS
        # NOTE SURFACE TILT MUST BE 0-180 DEGREES
        # NOTE WE CANNOT HAVE NEGATIVE VALUES
        return abs(recommended_surface_tilt)

    if mode == SurfacePositionOptimizerMode.Orientation:
        # NOTE INITIAL GUESS FOR SURFACE ORIENTATION OPTIMISATION
        # NOTE SURFACE ORIENTATION IS IN RADIANS
        # NOTE SURFACE ORIENTATION MUST BE BETWEEN 0-360 DEGREES
        # NOTE WE CANNOT HAVE NEGATIVE VALUES
        if latitude < 0:  # NOTE In southern hemisphere
            return 0 # NOTE radians
        
        return recommended_surface_orientation # NOTE in other case we are in the northern hemisphere
    
    if mode == SurfacePositionOptimizerMode.Orientation_and_Tilt:
        # NOTE INITIAL GUESS FOR SURFACE ORIENTATION OPTIMISATION
        # NOTE SURFACE ORIENTATION IS IN RADIANS
        # NOTE SURFACE ORIENTATION MUST BE BETWEEN 0-360 DEGREES
        # NOTE WE CANNOT HAVE NEGATIVE VALUES        
        if latitude < 0:  # NOTE In southern hemisphere
            return [
                0, # NOTE radians
                abs(recommended_surface_tilt), # NOTE radians
            ]

        return [
                recommended_surface_orientation, # NOTE radians
                abs(recommended_surface_tilt), # NOTE radians
            ]

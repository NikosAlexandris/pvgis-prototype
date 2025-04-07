from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.log import logger
from pvgisprototype.api.surface.parameter_models import SurfacePositionOptimizerMode


def build_location_dictionary(
    longitude,
    latitude,
    elevation,
    timestamps,
    timezone,
    surface_orientation,
    surface_tilt,
    mode,
    verbose,
):
    """
    """
    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(
            f"i Collect location parameters",
            alt=f"i [bold]Collect[/bold] the [magenta]location parameters[/magenta]"
        )
    location_parameters = {
        "longitude": longitude,
        "latitude": latitude,
        "elevation": elevation,
        "timestamps": timestamps,
        "timezone": timezone,
    }
    if mode == SurfacePositionOptimizerMode.Tilt:
        location_parameters["surface_orientation"] = surface_orientation

    if mode == SurfacePositionOptimizerMode.Orientation:
        location_parameters["surface_tilt"] = surface_tilt

    return location_parameters

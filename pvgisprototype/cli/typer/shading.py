from pvgisprototype.log import logger
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_shading
from pathlib import Path
from numpy import ndarray
from pvgisprototype.constants import DEGREES
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.core.arrays import create_array
import typer
from typer import Context
from numpy import fromstring
from xarray import DataArray
from pvgisprototype.constants import (
    DATA_TYPE_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    LOG_LEVEL_DEFAULT,
    DEGREES,
)


def parse_horizon_profile(
    horizon_profile_input: str | Path | None,
) -> Path | ndarray | None:
    """ """
    context_message = f"> Executing parser function : parse_horizon_profile()"
    context_message += f"\n  - Parameter input : {type(horizon_profile_input)} : {horizon_profile_input}"
    context_message_alternative = f"[yellow]>[/yellow] Executing [underline]parser function[/underline] : parse_horizon_profile()"
    # context_message_alternative += f'\n[yellow]i[/yellow] Callback parameter : {typer.CallbackParam}'
    context_message_alternative += f"\n  - Parameter input : {type(horizon_profile_input)} : {horizon_profile_input}"

    try:
        if isinstance(horizon_profile_input, (str, Path)):
            path = Path(horizon_profile_input)
            if path.exists():
                context_message += f"\n  < Returning object : {type(path)} : {path}"
                context_message_alternative += f"\n  < Returning object : {type(path)} : {path}"
                logger.info(context_message, alt=context_message_alternative)
                return path

        if isinstance(horizon_profile_input, str):
            # Add additional logic here for validity as an horizon profile ?
            horizon_profile_array = fromstring(horizon_profile_input, sep=",")
            if horizon_profile_array.size > 0:
                context_message += f"\n  < Returning object : {type(horizon_profile_array)} : {horizon_profile_array}"
                context_message_alternative += f"\n  < Returning object : {type(horizon_profile_array)} : {horizon_profile_array}"
                logger.info(context_message, alt=context_message_alternative)
                return horizon_profile_array
            else:
                logger.error("The input string could not be parsed into valid spectral factors.")
                raise ValueError(
                    "The input string could not be parsed into valid spectral factors."
                )
    except ValueError as e:
        logger.error(f"Error parsing input: {e}")
        return None


def horizon_profile_callback(
        ctx: Context,
        horizon_profile: Path | ndarray | None,
        ) -> DataArray:
    """Callback function to process spectral factor series argument."""
    context_message = f"> Executing callback function : horizon_profile_callback()"
    # context_message += f'\ni Callback parameter : {typer.CallbackParam}'
    context_message += f'\n  - Parameter input : {type(horizon_profile)} : {horizon_profile}'
    # context_message += f'\n  i Context : {ctx.params}'

    context_message_alternative = f"[yellow]>[/yellow] Executing [underline]callback function[/underline] : horizon_profile_callback()"
    # context_message_alternative += f'\n[yellow]i[/yellow] Callback parameter : {typer.CallbackParam}'
    if horizon_profile is None:
        # In order to avoid unbound errors
        # retrieve parameters from context
        timestamps = ctx.params.get("timestamps", None)
        dtype = ctx.params.get("dtype", DATA_TYPE_DEFAULT)
        array_backend = ctx.params.get("array_backend", ARRAY_BACKEND_DEFAULT)
        array_parameters = {
            "shape": timestamps.shape,
            "dtype": dtype,
            "init_method": "zeros",
            "backend": array_backend,
        }  # Borrow shape from timestamps
        context_message_alternative += f'\n  - Parameter input : {type(horizon_profile)} : {horizon_profile}'
        context_message_alternative += f'\n  [yellow]i[/yellow] [bold]Context[/bold] : {ctx.params}'
        
        logger.info(
                context_message,
                alt=context_message_alternative
                )
        return create_array(**array_parameters)

    else:
        if isinstance(horizon_profile, Path):
            from pvgisprototype.api.series.utilities import select_location_time_series
            # This _is_ a series, although NOT a _time_ series !
            longitude = ctx.params.get("longitude")
            latitude = ctx.params.get("latitude")
            neighbor_lookup = ctx.params.get("neighbor_lookup", NEIGHBOR_LOOKUP_DEFAULT)
            tolerance = ctx.params.get("tolerance", TOLERANCE_DEFAULT)
            mask_and_scale = ctx.params.get("mask_and_scale", MASK_AND_SCALE_FLAG_DEFAULT)
            in_memory = ctx.params.get("in_memory", IN_MEMORY_FLAG_DEFAULT)
            verbose = ctx.params.get("verbose", VERBOSE_LEVEL_DEFAULT)
            log = ctx.params.get("log", LOG_LEVEL_DEFAULT)
            horizon_profile = select_location_time_series(
                time_series=horizon_profile,
                variable=None,
                coordinate=None,
                minimum=None,
                maximum=None,
                longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
                latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                verbose=verbose,
                log=log,
            )
            return horizon_profile

        elif isinstance(horizon_profile, ndarray):
            return horizon_profile
        else:
            raise ValueError("Invalid horizon_profile type; expected Path, ndarray, or None.")

        # validate_horizon_profile()  # ?
        
        # # Validate that the data shape matches expected shape if applicable
        # if data_array.shape != some.shape:
        #     raise ValueError(f"Horizon profile shape {data_array.shape} does not match expected shape {some.shape}.")


typer_argument_horizon_profile = typer.Argument(
    help="Digital horizon model or a series of heights that form a horizon profile",
    # rich_help_panel=rich_help_panel_shading,
    parser=parse_horizon_profile,
    callback=horizon_profile_callback,
)
typer_option_horizon_profile = typer.Option(
    help="Digital horizon model or a series of heights that form a horizon profile",
    rich_help_panel=rich_help_panel_shading,
    parser=parse_horizon_profile,
    callback=horizon_profile_callback,
)
typer_option_shading_model = typer.Option(
    help="Model to calculate shading for the location in question",
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_shading,
)

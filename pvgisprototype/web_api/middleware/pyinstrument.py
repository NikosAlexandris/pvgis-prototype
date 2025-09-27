from fastapi import Request
from pvgisprototype.log import logger


async def profile_request_pyinstrument(request: Request, call_next, profile_output):
    """Profile the current request with pyinstrument.
    If provided format is not supported by profiler it uses the default: `json`
    Format `json` can be opened with [Speedscope.app](https://www.speedscope.app/)
    """
    from pyinstrument import Profiler
    from pyinstrument.renderers.html import HTMLRenderer
    from pyinstrument.renderers.speedscope import SpeedscopeRenderer

    default_format = "json"

    profile_type_to_ext = {"html": "html", "json": "speedscope.json"}
    profile_type_to_renderer = {
        "html": HTMLRenderer,
        "json": SpeedscopeRenderer,
    }

    with Profiler(interval=0.001, async_mode="enabled") as profiler:
        response = await call_next(request)

    extension = profile_type_to_ext.get(
        profile_output.lower(), profile_type_to_ext[default_format]
    )
    renderer = profile_type_to_renderer.get(
        profile_output.lower(), profile_type_to_renderer[default_format]
    )()

    if not profile_type_to_renderer.get(profile_output.lower()):
        logger.warning(
            f"Profile format {profile_output.lower()} is not supported. Using default {default_format} for PYINSTRUMENT."
        )
    with open(f"profile_pyinstrument.{extension}", "w") as out:
        out.write(profiler.output(renderer=renderer))

    return response

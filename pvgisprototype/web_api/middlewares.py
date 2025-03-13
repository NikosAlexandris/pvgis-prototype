import logging
from time import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Response
from pvgisprototype.core.caching import clear_cache_registry
from pvgisprototype.log import logger


class ClearCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Middleware to clear caches after each API request/response.
        """
        # from pvgisprototype.core.caching import inspect_cache_registry
        response: Response = await call_next(request)
        clear_cache_registry()

        return response


async def response_time_request(request: Request, call_next):
    """Middleware timing function to log request processing time."""
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    logger.debug(
        f"Request: {request.url.path} | Process time: {int(1000 * process_time)}ms"
    )

    return response


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


async def profile_request_scalene(request: Request, call_next):
    """Profile the current request with scalene.
    To profile using scalene run:
        `$scalene  --cli --json --outfile ./profile_scalene.json  pvgisprototype/webapi.py`
    and make the request. Otherwise, Scalene does not invoke properly. Currently only support for `json` is implemented.
    The `json` file can be opened with [Scalene Web UI](https://plasma-umass.org/scalene-gui/)
    """
    logger.warning("Scalene profiler doesn't work as expected!")

    from scalene.scalene_profiler import enable_profiling  # type: ignore

    with enable_profiling():
        response = await call_next(request)

    return response


async def profile_request_yappi(
        request: Request,
        call_next,
        profile_output: str = "pstat"):
    """Profile the current request with Yappi.

    Notes
    -----
    The supported formats are :

    - 'callgrind': For use with tools like KCachegrind/QCachegrind.
    - 'pstats': cProfile-compatible output.
    - 'json': For flamegraph visualization with [Speedscope](https://www.speedscope.app/).

    If requested format is not supported, the profiler uses `json`.

    """
    import yappi

    default_format = "pstat"
    profile_type_to_ext = {
        "callgrind": "callgrind.out",
        "pstat": "pstat",
    }
    profile_type_to_renderer = {
        "callgrind": "callgrind",
        "pstat": "pstat",
    }
    yappi.clear_stats()  # previous stats
    yappi.set_clock_type("cpu")  # use "wall" for wall time profiling

    yappi.start()
    response = await call_next(request)
    yappi.stop()

    func_stats = yappi.get_func_stats()

    # Determine output extension based on the profile format
    extension = profile_type_to_ext.get(profile_output.lower(), default_format)
    renderer = profile_type_to_renderer.get(profile_output.lower(), default_format)

    if not profile_type_to_renderer.get(profile_output.lower()):
        logger.warning(
            f"Profile format {profile_output.lower()} is not supported. Using default {default_format} for YAPPI."
        )

    with open(f"profile_yappi.{extension}", "w") as out:
        func_stats.save(out.name, type=renderer)

    return response


async def profile_request_functiontrace(request: Request, call_next):
    """Profile the current request with functiontrace."""
    import platform
    if platform.system() == 'Linux':

        try:
            import functiontrace
            functiontrace.trace()
            response = await call_next(request)
            logger.debug(f"Functiontrace completed for request : {request.url.path}")

            return response
        except:
            raise ImportError("Apparently `functiontrace` is not installed. Perhaps you want to install it first ?")
    else:
        raise OSError("`functiontrace` runs only on Linux and Mac OS.")


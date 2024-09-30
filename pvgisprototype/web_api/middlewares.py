from time import time
import logging
from fastapi import Request


logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)


async def response_time_request(request: Request, call_next):
    """Middleware timing function to log request processing time."""
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    logger.debug(f"Request: {request.url.path} | Process time: {int(1000 * process_time)}ms")

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

    profile_type_to_ext = {
        "html": "html", 
        "json": "speedscope.json"
    }
    profile_type_to_renderer = {
        "html": HTMLRenderer,
        "json": SpeedscopeRenderer,
    }

    with Profiler(interval=0.001, async_mode="enabled") as profiler:
        response = await call_next(request)

    extension = profile_type_to_ext.get(profile_output.lower(), profile_type_to_ext[default_format])
    renderer = profile_type_to_renderer.get(profile_output.lower(), profile_type_to_renderer[default_format])()

    if not profile_type_to_renderer.get(profile_output.lower()):
        logger.warning(f"Profile format {profile_output.lower()} is not supported. Using default {default_format} for PYINSTRUMENT.")
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

    from scalene.scalene_profiler import enable_profiling # type: ignore
            
    with enable_profiling():
        # Execute the request
        response = await call_next(request)

    return response

async def profile_request_yappi(request: Request, call_next, profile_output):
    """
    Profile the current request with Yappi.
    If provided format is not supported by profiler it uses the default: `json`
    Supported formats:
    - 'callgrind': For use with tools like KCachegrind/QCachegrind.
    - 'pstats': cProfile-compatible output.
    - 'json': For flamegraph visualization with [Speedscope](https://www.speedscope.app/).
    """
    import yappi
    default_format = "pstat"

    # Mapping profile output type to file extensions and Yappi save types
    profile_type_to_ext = {
        "callgrind": "callgrind.out",
        "pstat": "pstat",
    }
    profile_type_to_renderer = {
        "callgrind": "callgrind",
        "pstat": "pstat",
    }
    # Start Yappi profiler (CPU clock type)
    yappi.clear_stats()  # Clear previous stats
    yappi.set_clock_type("cpu")  # You can also use "wall" for wall time profiling
    yappi.start()

    # Process the request
    response = await call_next(request)

    # Stop the profiler
    yappi.stop()

    # Get function stats
    func_stats = yappi.get_func_stats()

    # Determine the output extension based on the profile format
    extension = profile_type_to_ext.get(profile_output.lower(), default_format)
    renderer = profile_type_to_renderer.get(profile_output.lower(), default_format)
    
    if not profile_type_to_renderer.get(profile_output.lower()):
        logger.warning(f"Profile format {profile_output.lower()} is not supported. Using default {default_format} for YAPPI.")

    # Save the profile output in the selected format
    with open(f"profile_yappi.{extension}", "w") as out:
        func_stats.save(out.name, type=renderer)

    return response
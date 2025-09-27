from fastapi import Request
from pvgisprototype.log import logger


async def profile_request_yappi(
    request: Request, call_next, profile_output: str = "pstat"
):
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




from fastapi import Request
from pvgisprototype.log import logger


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

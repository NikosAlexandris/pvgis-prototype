from fastapi import Request
from pvgisprototype.log import logger


async def profile_request_functiontrace(request: Request, call_next):
    """Profile the current request with functiontrace."""
    import platform

    if platform.system() == "Linux":

        try:
            import functiontrace

            functiontrace.trace()
            response = await call_next(request)
            logger.debug(f"Functiontrace completed for request : {request.url.path}")

            return response
        except:
            raise ImportError(
                "Apparently `functiontrace` is not installed. Perhaps you want to install it first ?"
            )
    else:
        raise OSError("`functiontrace` runs only on Linux and Mac OS.")

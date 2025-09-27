import traceback
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from pvgisprototype.log import logger
from time import time


async def response_time_request(request: Request, call_next):
    """Middleware timing function to log request processing time."""
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    logger.debug(
        f"Request: {request.url.path} | Process time: {int(1000 * process_time)}ms"
    )

    return response


class LogRequestIDMiddleware(BaseHTTPMiddleware):
    """
    Adds a request ID to the request state and logs the request to the access and error log.
    """

    async def dispatch(
        self,
        request: Request,
        call_next,
        access_log="pvgis.access",
        error_log="pvgis.error",
    ):
        """
        Handle the request and assign a unique request ID to the request state.
        Logs the request to the access log and if an exception occurs, logs the
        exception to the error log. In every case the request ID is logged.

        Parameters
        ----------
        request : Request
            The request object
        call_next : Callable[[Request], Awaitable[Response]]
            The next function to call in the middleware chain
        access_log : str, optional
            The name of the access log, by default "pvgis.access"
        error_log : str, optional
            The name of the error log, by default "pvgis.error"

        Returns
        -------
        Response
            The response to the request
        """
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        try:
            # NOTE Bind the request_id during the entire request lifecycle
            with logger.contextualize(request_id=request_id):
                response = await call_next(request)

                # NOTE Log successful response
                logger.bind(name=access_log).info(
                    f'{request.client.host}:{request.client.port} - "{request.method} {request.url.path}?{request.url.query}" {response.status_code}'  # type: ignore[union-attr]
                )

                return response

        except Exception as exception:
            with logger.contextualize(request_id=request_id):

                # NOTE Error log (500 error), include traceback and custom name
                logger.bind(name=access_log).opt(exception=exception).error(
                    f'{request.client.host}:{request.client.port} - "{request.method} {request.url.path}?{request.url.query}" 500'  # type: ignore[union-attr]
                )
                logger.bind(name=error_log).error(
                    "".join(
                        traceback.format_exception(
                            type(exception), exception, exception.__traceback__
                        )
                    )
                )
            raise  # NOTE let FastAPI handle the response generation

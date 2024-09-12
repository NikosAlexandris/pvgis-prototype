from time import time
import logging
from fastapi import Request

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

async def response_time(request: Request, call_next):
    """Middleware timing function to log request processing time."""
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    logger.debug(f"Request: {request.url.path} | Process time: {int(1000 * process_time)}ms")

    return response
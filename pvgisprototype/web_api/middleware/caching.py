"""
Middleware to manage per-request cache lifecycle.
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from pvgisprototype.core.caching import (
    clear_request_caches,
    # get_request_cache_registry, 
    get_request_id
)
import gc
from pvgisprototype.log import logger
import os


class CacheLifecycleMiddleware(BaseHTTPMiddleware):
    """Simple middleware to clear request caches after completion"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        #request_cache_registry = get_request_cache_registry()
        #request_id = id(cache)
        pid = os.getpid()
        #logger.debug(f"🚀 [PID:{pid}] Starting request with cache ID: {request_id}")
        
        try:
            response: Response = await call_next(request)
            duration = time.time() - start_time
            logger.debug(f"Request completed in {duration:.3f}s")
            return response
            
        except Exception as e:
            # logger.error(f"Request failed: {e}")
            logger.error(f"❌ [PID:{pid}] Request failed: {e}")
            raise
            
        finally:
            # Always clear request caches
            request_id = get_request_id()
            clear_request_caches()
            gc.collect()
            #logger.debug(f"✅ [PID:{pid}] Request completed, cache {cache} cleared for ID: {request_id}")
            logger.debug(f"✅ [PID:{pid}] Caching lifecycle for ID {request_id} complete.-")

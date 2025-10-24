from pvgisprototype.log import logger
from contextlib import asynccontextmanager
from pvgisprototype.log import initialize_web_api_logger

from pvgisprototype.web_api.cache.caching import set_cache_backend
from aiocache import Cache
import traceback

from pvgisprototype.web_api.fastapi.extended import ExtendedFastAPI

from pvgisprototype.web_api.dependency.common_datasets import _provide_common_datasets
from pvgisprototype.constants import (
    IN_MEMORY_FLAG_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.api.series.time_series import (
    get_time_series_as_arrays_or_sets,
)


@asynccontextmanager
async def configure_application(app: ExtendedFastAPI):
    """Enhanced lifespan with Redis cache initialization."""
    
    # Initialize Loguru for FastAPI & Uvicorn
    initialize_web_api_logger(
        log_level=app.settings.LOG_LEVEL,
        # log_format=app.settings.LOG_FORMAT,
        rich_handler=app.settings.USE_RICH,
        server=app.settings.WEB_SERVER,
        access_log_path=app.settings.ACCESS_LOG_PATH,
        error_log_path=app.settings.ERROR_LOG_PATH,
        rotation=app.settings.ROTATION,
        retention=app.settings.RETENTION,
        compression=app.settings.COMPRESSION,
        log_console=app.settings.LOG_CONSOLE,
        diagnose=app.settings.LOG_DIAGNOSE,
    )

    # Debug: Print cache-related settings
    logger.info(f"🔧 Cache Configuration Debug:")
    logger.info(f"   REDIS_ENABLED: {getattr(app.settings, 'REDIS_ENABLED', 'NOT_SET')}")
    logger.info(f"   REDIS_HOST: {getattr(app.settings, 'REDIS_HOST', 'NOT_SET')}")
    logger.info(f"   REDIS_PORT: {getattr(app.settings, 'REDIS_PORT', 'NOT_SET')}")
    logger.info(f"   REDIS_DB: {getattr(app.settings, 'REDIS_DB', 'NOT_SET')}")
    logger.info(f"   REDIS_TTL: {getattr(app.settings, 'REDIS_TTL', 'NOT_SET')}")

    # Configure cache backend based on settings
    try:
        redis_enabled = getattr(app.settings, 'REDIS_ENABLED', False)
        
        if redis_enabled:
            logger.info("🚀 Attempting to configure Redis cache...")
            
            # Test Redis connection with more detailed error handling
            redis_test = Cache(
                Cache.REDIS,
                endpoint=getattr(app.settings, 'REDIS_HOST', '127.0.0.1'),
                port=getattr(app.settings, 'REDIS_PORT', 6379),
                db=getattr(app.settings, 'REDIS_DB', 0)
            )
            
            logger.info(f"🔌 Testing Redis connection to {app.settings.REDIS_HOST}:{app.settings.REDIS_PORT}...")
            
            # Test connection with a simple ping
            await redis_test.set("test_connection", "ok", ttl=5)
            test_value = await redis_test.get("test_connection")
            await redis_test.delete("test_connection")
            
            if test_value == "ok":
                # Configure Redis caching
                redis_config = {
                    "endpoint": getattr(app.settings, 'REDIS_HOST', '127.0.0.1'),
                    "port": getattr(app.settings, 'REDIS_PORT', 6379),
                    "db": getattr(app.settings, 'REDIS_DB', 0),
                    "ttl": getattr(app.settings, 'REDIS_TTL', 3600)
                }
                set_cache_backend(use_redis=True, redis_config=redis_config)
                logger.info("✅ Redis cache enabled and tested successfully!")
                logger.info(f"   📊 Cache TTL: {redis_config['ttl']} seconds")
                logger.info(f"   🎯 Redis DB: {redis_config['db']}")

                # In your startup/lifespan function, after calling set_cache_backend
                from pvgisprototype.web_api.cache.redis import USE_REDIS_CACHE
                logger.info(f"🔧 Final USE_REDIS_CACHE state: {USE_REDIS_CACHE}")
            else:
                raise Exception("Redis connection test failed - test value mismatch")
                
        else:
            set_cache_backend(use_redis=False)
            logger.info("📦 Using LRU cache (Redis disabled in configuration)")
            
    except Exception as e:
        logger.error(f"❌ Redis cache setup failed: {e}")
        logger.error(f"🔍 Full error: {traceback.format_exc()}")
        logger.warning("⚠️  Falling back to LRU cache...")
        set_cache_backend(use_redis=False)

    # Pre-open datasets at startup
    try:
        common_datasets = await _provide_common_datasets()
        app.state.preopened_datasets = get_time_series_as_arrays_or_sets(common_datasets)
        # Pre-open all datasets
        app.state.preopened_datasets = get_time_series_as_arrays_or_sets(
            common_datasets,
            mask_and_scale=MASK_AND_SCALE_FLAG_DEFAULT,
            in_memory=IN_MEMORY_FLAG_DEFAULT,
            verbose=VERBOSE_LEVEL_DEFAULT,
        )

        logger.debug("✅ Opened all datasets successfully")

    except Exception as e:
        logger.warning(f"⚠️ Failed to open datasets: {e}")
        app.state.preopened_datasets = None

    yield  # Application runs here

    # Cleanup on shutdown
    if hasattr(app.state, "preopened_datasets"):
        app.state.preopened_datasets = None
        logger.info("🧹 Cleaned up application state")

from datetime import time, timedelta
from pathlib import Path

from pydantic_settings import BaseSettings

from pvgisprototype.web_api.config.options import LogFormat, LogLevel
from pvgisprototype.web_api.config.settings import (
    LOG_FORMAT_DEFAULT,
    LOG_LEVEL_DEFAULT,
    PROFILING_ENABLED_PRODUCTION_DEFAULT,
)


class CommonSettings(BaseSettings):

    PROFILING_ENABLED: bool = PROFILING_ENABLED_PRODUCTION_DEFAULT
    LOG_LEVEL: LogLevel = LOG_LEVEL_DEFAULT
    USE_RICH: bool = False
    WEB_SERVER: str = "uvicorn"
    LOG_FORMAT: LogFormat = LOG_FORMAT_DEFAULT
    ACCESS_LOG_PATH: str | None = None
    ERROR_LOG_PATH: str | None = None
    ROTATION: str | int | time | timedelta | None = None
    RETENTION: str | int | timedelta | None = None
    COMPRESSION: str | None = None
    LOG_CONSOLE: bool = True

#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
from datetime import time, timedelta
from pydantic_settings import BaseSettings
from pvgisprototype.web_api.config.options import DataReadMode, LogFormat, LogLevel
from pvgisprototype.web_api.config.settings import (
    LOG_FORMAT_DEFAULT,
    LOG_LEVEL_DEFAULT,
    PROFILING_ENABLED_PRODUCTION_DEFAULT,
)


class CommonSettings(BaseSettings):

    PROFILING_ENABLED: bool = PROFILING_ENABLED_PRODUCTION_DEFAULT
    LOG_LEVEL: LogLevel = LOG_LEVEL_DEFAULT
    USE_RICH: bool = False
    DATA_READ_MODE: DataReadMode = DataReadMode.ASYNC
    WEB_SERVER: str = "uvicorn"
    LOG_FORMAT: LogFormat = LOG_FORMAT_DEFAULT
    ACCESS_LOG_PATH: str | None = None
    ERROR_LOG_PATH: str | None = None
    ROTATION: str | int | time | timedelta | None = None
    RETENTION: str | int | timedelta | None = None
    COMPRESSION: str | None = None
    LOG_CONSOLE: bool = True
    LOG_DIAGNOSE: bool = True

    # Redis Cache Configuration
    REDIS_ENABLED: bool = True  # Default disabled
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_TTL: int = 3600

    class Config:
        # mapping, example : PVGIS_WEBAPI_REDIS_ENABLED -> REDIS_ENABLED
        env_prefix = "PVGIS_WEBAPI_"

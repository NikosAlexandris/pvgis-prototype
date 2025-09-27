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
from pydantic import Field
from pvgisprototype.web_api.config.base import CommonSettings
from pvgisprototype.web_api.config.options import LogLevel
from pvgisprototype.web_api.config.options import Profiler
from pvgisprototype.web_api.config.options import ProfileOutput
from pvgisprototype.web_api.config.options import DataReadMode

from pvgisprototype.web_api.config.settings import (
    PROFILING_ENABLED_DEVELOPMENT_DEFAULT,
    LOG_LEVEL_DEVELOPMENT_DEFAULT,
    MEASURE_REQUEST_TIME_DEVELOPMENT_DEFAULT,
    PROFILER_DEVELOPMENT_DEFAULT,
    PROFILE_OUTPUT_DEVELOPMENT_DEFAULT,
)


class DevelopmentSettings(CommonSettings):

    PROFILING_ENABLED: bool = PROFILING_ENABLED_DEVELOPMENT_DEFAULT
    LOG_LEVEL: LogLevel = LOG_LEVEL_DEVELOPMENT_DEFAULT
    MEASURE_REQUEST_TIME: bool = MEASURE_REQUEST_TIME_DEVELOPMENT_DEFAULT
    PROFILER: Profiler = PROFILER_DEVELOPMENT_DEFAULT
    PROFILE_OUTPUT: ProfileOutput = PROFILE_OUTPUT_DEVELOPMENT_DEFAULT
    ACCESS_LOG_PATH: str = Field(
        default="access.log", env="PVGIS_WEB_API_ACCESS_LOG_PATH"
    )
    ERROR_LOG_PATH: str = Field(default="error.log", env="PVGIS_WEB_API_ERROR_LOG_PATH")
    LOG_CONSOLE: bool = Field(default=True, env="PVGIS_WEB_API_LOG_CONSOLE")
    DATA_READ_MODE: DataReadMode = Field(
        default=DataReadMode.ASYNC, env="PVGIS_WEB_API_DATA_READ_MODE"
    )


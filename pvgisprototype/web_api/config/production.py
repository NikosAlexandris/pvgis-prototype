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
from pvgisprototype.web_api.config.settings import (
    MEASURE_REQUEST_TIME_PRODUCTION_DEFAULT,
)
from pvgisprototype.web_api.config.options import DataReadMode


class ProductionSettings(CommonSettings):
    MEASURE_REQUEST_TIME: bool = MEASURE_REQUEST_TIME_PRODUCTION_DEFAULT
    ACCESS_LOG_PATH: str = Field(
        default="access.log", env="PVGIS_WEB_API_ACCESS_LOG_PATH"
    )
    ERROR_LOG_PATH: str = Field(default="error.log", env="PVGIS_WEB_API_ERROR_LOG_PATH")
    LOG_CONSOLE: bool = Field(default=False, env="PVGIS_WEB_API_LOG_CONSOLE")
    DATA_READ_MODE: DataReadMode = Field(
        default=DataReadMode.ASYNC, env="PVGIS_WEB_API_DATA_READ_MODE"
    )
    LOG_DIAGNOSE: bool = False

    class Config:
        env_prefix = "PVGIS_WEB_API_"

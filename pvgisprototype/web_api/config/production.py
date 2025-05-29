from pydantic import Field
from pvgisprototype.web_api.config.base import CommonSettings
from pvgisprototype.web_api.config.settings import (
    MEASURE_REQUEST_TIME_PRODUCTION_DEFAULT,
)


class ProductionSettings(CommonSettings):
    MEASURE_REQUEST_TIME: bool = MEASURE_REQUEST_TIME_PRODUCTION_DEFAULT
    ACCESS_LOG_PATH: str = Field(
        default="access.log", env="PVGIS_WEB_API_ACCESS_LOG_PATH"
    )
    ERROR_LOG_PATH: str = Field(default="error.log", env="PVGIS_WEB_API_ERROR_LOG_PATH")
    LOG_CONSOLE: bool = Field(default=False, env="PVGIS_WEB_API_LOG_CONSOLE")

    class Config:
        env_prefix = "PVGIS_WEB_API_"

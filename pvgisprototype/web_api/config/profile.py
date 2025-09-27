from pydantic import Field
from pvgisprototype.web_api.config.base import CommonSettings
from pvgisprototype.web_api.config.settings import (
    PROFILING_ENABLED_DEVELOPMENT_DEFAULT,
    MEASURE_REQUEST_TIME_DEVELOPMENT_DEFAULT,
    PROFILER_DEVELOPMENT_DEFAULT,
    PROFILE_OUTPUT_DEVELOPMENT_DEFAULT,
)
from pvgisprototype.web_api.config.options import Profiler
from pvgisprototype.web_api.config.options import ProfileOutput
from pvgisprototype.web_api.config.options import DataReadMode


class ProfileSettings(CommonSettings):
    MEASURE_REQUEST_TIME: bool = MEASURE_REQUEST_TIME_DEVELOPMENT_DEFAULT
    PROFILING_ENABLED: bool = PROFILING_ENABLED_DEVELOPMENT_DEFAULT
    PROFILER: Profiler = PROFILER_DEVELOPMENT_DEFAULT
    PROFILE_OUTPUT: ProfileOutput = PROFILE_OUTPUT_DEVELOPMENT_DEFAULT
    ACCESS_LOG_PATH: str = Field(
        default="access.log", env="PVGIS_WEB_API_ACCESS_LOG_PATH"
    )
    ERROR_LOG_PATH: str = Field(default="error.log", env="PVGIS_WEB_API_ERROR_LOG_PATH")
    LOG_CONSOLE: bool = Field(default=False, env="PVGIS_WEB_API_LOG_CONSOLE")
    DATA_READ_MODE: DataReadMode = Field(
        default=DataReadMode.ASYNC, env="PVGIS_WEB_API_DATA_READ_MODE"
    )

    class Config:
        env_prefix = "PVGIS_WEB_API_"

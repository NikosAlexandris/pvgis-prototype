from pvgisprototype.web_api.config.base import CommonSettings
from pvgisprototype.web_api.config.options import LogLevel
from pvgisprototype.web_api.config.options import Profiler
from pvgisprototype.web_api.config.options import ProfileOutput

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

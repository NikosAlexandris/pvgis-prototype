from pydantic_settings import BaseSettings

from pvgisprototype.web_api.config.settings import (
    LOG_LEVEL_DEFAULT,
    PROFILING_ENABLED_PRODUCTION_DEFAULT,
    LOG_FORMAT_DEFAULT,
)
from pvgisprototype.web_api.config.options import (
    LogLevel,
    LogFormat,
)

class CommonSettings(BaseSettings):

    PROFILING_ENABLED: bool = PROFILING_ENABLED_PRODUCTION_DEFAULT
    LOG_LEVEL: LogLevel = LOG_LEVEL_DEFAULT
    LOG_FORMAT:LogFormat = LOG_FORMAT_DEFAULT

    

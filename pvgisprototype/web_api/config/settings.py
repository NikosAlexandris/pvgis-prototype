from pvgisprototype.web_api.config.options import (
    Profiler,
    ProfileOutput,
)
from pvgisprototype.web_api.config.options import (
    LogLevel,
    LogFormat,
)

# Common default settings
LOG_LEVEL_DEFAULT = LogLevel.error
PROFILING_ENABLED_PRODUCTION_DEFAULT = False
LOG_FORMAT_DEFAULT = LogFormat.uvicorn

# Development default settings
LOG_LEVEL_DEVELOPMENT_DEFAULT = LogLevel.debug
PROFILING_ENABLED_DEVELOPMENT_DEFAULT = True
PROFILER_DEVELOPMENT_DEFAULT = Profiler.pyinstrument
PROFILE_OUTPUT_DEVELOPMENT_DEFAULT = ProfileOutput.json
MEASURE_REQUEST_TIME_DEVELOPMENT_DEFAULT = True

# Production default settings
MEASURE_REQUEST_TIME_PRODUCTION_DEFAULT = False

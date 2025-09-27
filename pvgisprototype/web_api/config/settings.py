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
from pvgisprototype.web_api.config.options import (
    LogFormat,
    LogLevel,
    ProfileOutput,
    Profiler,
)

# Common default settings
LOG_LEVEL_DEFAULT = LogLevel.info
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

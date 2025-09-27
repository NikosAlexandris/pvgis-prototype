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
from functools import lru_cache
from os import environ, path

from dotenv import load_dotenv

import logging
from pvgisprototype.web_api.config.development import DevelopmentSettings
from pvgisprototype.web_api.config.options import Environment
from pvgisprototype.web_api.config.production import ProductionSettings
from pvgisprototype.web_api.config.profile import ProfileSettings

LOGGER = "uvicorn"


def get_environment():

    load_dotenv(path.join(path.dirname(path.abspath(__file__)), "../../../.env"))
    try:
        return environ["PVGISPROTOTYPE_WEB_API_ENVIRONMENT"]
    except KeyError:
        return "Production"  # NOTE IS THIS OK? FORCING PRODUCTION CONFIGURATION IF NO ENVIROMENTAL VARIABLE PVGISPROTOTYPE_WEB_API_ENVIRONMENT IS PROVIDED


@lru_cache
def get_settings():
    logger = logging.getLogger(LOGGER)
    logger.info(f"Environment: {get_environment()}")
    match get_environment():
        case Environment.Production:
            return ProductionSettings()
        case Environment.Development:
            return DevelopmentSettings()
        case Environment.Profile:
            return ProfileSettings()
        case _:
            logger.error(
                f"⚠️ Invalid environment: {get_environment()}, continuing with ProductionSettings"
            )
            return ProductionSettings()

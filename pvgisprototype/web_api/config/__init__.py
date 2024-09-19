from functools import lru_cache
from dotenv import load_dotenv
from os import environ
from os import path
from pvgisprototype.web_api.config.development import DevelopmentSettings
from pvgisprototype.web_api.config.production import ProductionSettings
from pvgisprototype.web_api.config.options import Environment

def get_environment():
    
    load_dotenv(path.join(path.dirname(path.abspath(__file__)), "../../../.env"))
    return environ["PVGISPROTOTYPE_WEB_API_ENVIRONMENT"]

@lru_cache
def get_settings():
    match get_environment():
        case Environment.production:
            return ProductionSettings()
        case _:
            return DevelopmentSettings()
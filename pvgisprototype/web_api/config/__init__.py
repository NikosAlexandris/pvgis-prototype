from functools import lru_cache
from dotenv import load_dotenv
from os import environ
from os import path
from pvgisprototype.web_api.config.development import DevelopmentSettings
from pvgisprototype.web_api.config.production import ProductionSettings
from pvgisprototype.web_api.config.options import Environment

def get_environment():
    
    load_dotenv(path.join(path.dirname(path.abspath(__file__)), "../../../.env"))
    try:
        return environ["PVGISPROTOTYPE_WEB_API_ENVIRONMENT"]
    except KeyError:
        return "Production" #NOTE IS THIS OK? FORCING PRODUCTION CONFIGURATION IF NO ENVIROMENTAL VARIABLE PVGISPROTOTYPE_WEB_API_ENVIRONMENT IS PROVIDED
    
@lru_cache
def get_settings():
    match get_environment():
        case Environment.Production:
            return ProductionSettings()
        case _:
            return DevelopmentSettings()

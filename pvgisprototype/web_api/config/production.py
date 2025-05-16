from pvgisprototype.web_api.config.base import CommonSettings
from pvgisprototype.web_api.config.settings import (
    MEASURE_REQUEST_TIME_PRODUCTION_DEFAULT,
)


class ProductionSettings(CommonSettings):
    MEASURE_REQUEST_TIME: bool = MEASURE_REQUEST_TIME_PRODUCTION_DEFAULT
    ACCESS_LOG_PATH: str = "access.log"
    ERROR_LOG_PATH: str = "error.log"

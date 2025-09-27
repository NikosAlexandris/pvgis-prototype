from fastapi import FastAPI
from pvgisprototype.web_api.config.base import CommonSettings
from pvgisprototype.web_api.config import Environment


class ExtendedFastAPI(FastAPI):
    def __init__(
        self, settings: CommonSettings, environment: Environment, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.settings = settings
        self.environment = environment

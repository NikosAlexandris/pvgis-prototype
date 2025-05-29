import multiprocessing

from gunicorn.glogging import Logger as GunicornLogger

from pvgisprototype.log import initialize_web_api_logger, logger


class StubbedGunicornLogger(GunicornLogger):
    def setup(self, cfg):
        super().setup(cfg)
        for handler in self.error_log.handlers[:]:
            self.error_log.removeHandler(handler)
        self.error_log.propagate = True
        logger.debug("StubbedGunicornLogger initialized")


initialize_web_api_logger(server="gunicorn")

logger_class = StubbedGunicornLogger
errorlog = "-"
accesslog = None

bind = "127.0.0.1:9060"
workers = (multiprocessing.cpu_count() * 2) + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 300

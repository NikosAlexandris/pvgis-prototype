import logging


logger = logging.getLogger()
logger_config=logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s, %(msecs)d; %(levelname)-8s; %(lineno)4d: %(message)s",
        datefmt="%I:%M:%S",
        )

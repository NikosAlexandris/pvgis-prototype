from rich.logging import RichHandler
from loguru import logger
logger.remove()  # the default handler
logger.add(RichHandler())

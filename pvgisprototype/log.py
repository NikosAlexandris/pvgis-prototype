"""
Attention : This should be part of the main() function, that is : a global
logging mechanism and configuration.
"""
from loguru import logger


logger.remove()  # Remove default handler
logger.add(logfile, enqueue=True, backtrace=True, diagnose=True)

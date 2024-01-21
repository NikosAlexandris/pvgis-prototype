"""
Attention : This should be part of the main() function, that is : a global
logging mechanism and configuration.
"""
from loguru import logger


logger.remove()  # Remove default handler


def filter_function(record):
    """Determine which logs to include based on the verbosity level."""
    # Assuming record["level"].name gives the log level like "INFO", "DEBUG", etc.
    # return verbose
    return record["level"].name == "INFO" if verbosity_level == 1 else True


def initialize_logger(
    # logfile: Optional[Path] = None,
):
    """
    Initialise logging to either stderr or a file ?
    """
    log_file = "kerchunking_{time}.log"
    # if logfile:
    # logger.add(logfile, enqueue=True, backtrace=True, diagnose=True)
    logger.add(log_file, filter=filter_function)  # , compression="tar.gz")
    
    # else:
    #     import sys
    #     logger.add(sys.stderr, enqueue=True, backtrace=True, diagnose=True)

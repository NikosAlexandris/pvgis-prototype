"""
Attention : This should be part of the main() function, that is : a global
logging mechanism and configuration.
"""
import richuru
richuru.install()
from loguru import logger
from functools import wraps
    
from pvgisprototype.validation.hashing import generate_hash
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL


def initialize_logger(
    log_file = None,
    verbosity_level=0,
    rich_handler: bool = False,
):
    """
    Initialise logging to either stderr or a file ?
    """
    def filter_function(record):
        """Determine which logs to include based on the verbosity level."""
        return record["level"].name == "INFO" if verbosity_level == 1 else True

    if rich_handler:
        logger.remove()
        from rich.logging import RichHandler
        logger.add(RichHandler(), filter=filter_function)

    if log_file:
        log_file = "pvgisprototype_{time}.log"
        logger.add(log_file, filter=filter_function)  # , compression="tar.gz")
        # logger.add(logfile, enqueue=True, backtrace=True, diagnose=True)

    # else:
    #     import sys
    #     logger.add(sys.stderr, enqueue=True, backtrace=True, diagnose=True)


def log_function(
        verbosity_level,
        data_type,
):
    """
    """
    if verbosity_level > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        import inspect
        caller_name = inspect.stack()[1].function
        logger.info(
                f"Call : {caller_name}() | Requested data type : {data_type}",
                alt=f"Call {caller_name}(), Requested data type : [reverse]{data_type}[/reverse]"
            )


def log_function_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        verbosity_level = kwargs.get('log', 0)
        if verbosity_level > HASH_AFTER_THIS_VERBOSITY_LEVEL:
            data_type = kwargs.get('dtype', None)
            logger.info(
                    f"Call : {func.__name__}() | Requested data type : {data_type}",
                    alt=f"Call {func.__name__}(), Requested data type : [reverse]{data_type}[/reverse]"
                )
        return func(*args, **kwargs)

        # if verbosity_level > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        #     logger.debug(f"Function {func.__name__} completed with locals: {locals()}")

    return wrapper


def log_data_fingerprint(
        data,
        log_level,
        hash_after_this_verbosity_level=2,
):
    """
    """
    if log_level > hash_after_this_verbosity_level:
        import inspect
        caller_name = inspect.stack()[1].function
        data_hash = generate_hash(data)
        logger.info(
                f"Output of {caller_name}() : {type(data)}, {data.dtype}, Hash {data_hash}",
                alt = f"Output of {caller_name}() : {type(data)}, [reverse]{data.dtype}[/reverse], Hash [code]{data_hash}[/code]"
        )
    if log_level > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        from devtools import debug
        debug(locals())

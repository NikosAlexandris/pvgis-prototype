"""
Attention : This should be part of the main() function, that is : a global
logging mechanism and configuration.
"""
# import richuru
# richuru.install()
from loguru import logger
print("Logger initialized!")
from functools import wraps
from pvgisprototype.validation.hashing import generate_hash
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL


import traceback


from typer import Context
# Attention : Used in typer_option_log !
def initialize_logger(
    ctx: Context,
    log_level: int = 0,
    # log_file: bool = None,
    # verbosity_level: int = 0,
    # rich_handler: bool = False,
):
    """
    Initialise logging to either stderr or a file ?

    Notes
    -----
    Attention : Used in typer_option_log !

    """
    # print(f'Remove logger')
    logger.remove()
    # print(f'Caller command name : {ctx.command.name}')
    # print(f"Command path : {ctx.command_path}")
    # print(f"info_name : {ctx.info_name}")
    # print(f"params : {ctx.params}")

    LOGURU_LEVELS = {
        0: "WARNING",  # Only show warnings and errors by default
        1: "INFO",     # Show info, warnings, and errors if log level is 1 or higher
        # Define more levels as needed
        7: "DEBUG",    # Show debug messages only if log level is 7 or higher
    }
    minimum_log_level = LOGURU_LEVELS.get(log_level, "WARNING")
    # print(f'Minimum log level : {minimum_log_level}')

    rich_handler = ctx.params.get('log_rich_handler')
    if rich_handler:
        print(f'RichHandler')
        from rich.logging import RichHandler
        logger.add(RichHandler(), level=minimum_log_level)

    log_file = ctx.params.get('log_file')
    if log_file:
        log_file = "pvgisprototype_{time}.log"
        logger.add(log_file, level=minimum_log_level)  # , compression="tar.gz")
        logger.info(f'Logging to file : {log_file}', alt=f'Logging to file : [reverse]{log_file}[/reverse] ?')

    if log_level > 0:
        print(f'Logging to sys.stderr')
        import sys
        # logger.add(sys.stderr, enqueue=True, backtrace=True, diagnose=True)
        logger.add(sys.stderr, level=minimum_log_level)

    return log_level


def log_function_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        verbosity_level = kwargs.get('log', 0) or 0
        if verbosity_level > HASH_AFTER_THIS_VERBOSITY_LEVEL:
            data_type = kwargs.get('dtype', None)
            logger.info(
                    f"> Call : {func.__name__}(), Requested data type : {data_type}",
                    alt=f"> Call {func.__name__}(), Requested data type : [reverse]{data_type}[/reverse]"
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
                f"< Output {caller_name}() : {type(data)}, {data.dtype}, Hash {data_hash}",
                alt = f"< [bold]Output[/bold] of {caller_name}() : {type(data)}, [reverse]{data.dtype}[/reverse], Hash [code]{data_hash}[/code]"
        )
    if log_level > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        from devtools import debug
        debug(locals())

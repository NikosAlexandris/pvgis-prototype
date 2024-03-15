"""
Attention : This should be part of the main() function, that is : a global
logging mechanism and configuration.
"""
from loguru import logger
logger.remove()
from functools import wraps
from pvgisprototype.validation.hashing import generate_hash
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
import traceback


from typer import Context
def initialize_logger(
    ctx: Context,
    log_level: int = 0,
):
    """
    Initialise logging to either stderr or a file ?

    Notes
    -----
    Attention : Used in typer_option_log !

    """
    # import richuru
    # richuru.install()
    # print(f'Remove logger')
    # logger.remove()
    # import richuru
    # richuru.install()
    # print(f'Caller command name : {ctx.command.name}')
    # print(f"Command path : {ctx.command_path}")
    # print(f"info_name : {ctx.info_name}")
    # print(f"params : {ctx.params}")

    LOGURU_LEVELS = {
        0: "WARNING",  # Only show warnings and errors
        1: "INFO",     # Show info, warnings, and errors
        # Define more levels ?
        7: "DEBUG",    # Show debug messages
    }
    minimum_log_level = LOGURU_LEVELS.get(log_level, "WARNING")
    # print(f'Minimum log level : {minimum_log_level}')

    rich_handler = ctx.params.get('log_rich_handler')
    if rich_handler:
        print(f'RichHandler')
        logger.remove()
        from rich.logging import RichHandler
        logger.add(RichHandler(), level=minimum_log_level)

    log_file = ctx.params.get('log_file')
    if log_file:
        # print(f'Logging to file : {log_file}', alt=f'Logging to file : [reverse]{log_file}[/reverse] ?')
        # logger.remove()
        log_file = "pvgisprototype_{time}.log"
        logger.add(log_file, level=minimum_log_level)  # , compression="tar.gz")
        # logger.info(f'Logging to file : {log_file}', alt=f'Logging to file : [reverse]{log_file}[/reverse] ?')

    if log_level > 0:
        print(f'Logging to sys.stderr')
        logger.remove()
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
        output=None,
):
    """
    """
    if output:
        print(type(output))
    if log_level > hash_after_this_verbosity_level:
        import inspect
        caller_name = inspect.stack()[1].function
        data_hash = generate_hash(data)
        logger.info(
                f"< Output {caller_name}() : {type(data)}, {data.dtype}, Hash {data_hash}",
                # alt = f"< [bold]Output[/bold] of {caller_name}() : {type(data)}, [reverse]{data.dtype}[/reverse], Hash [code]{data_hash}[/code]",
        )
    if log_level > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        from devtools import debug
        debug(locals())

"""
Attention : This should be part of the main() function, that is : a global
logging mechanism and configuration.
"""
import logging
from loguru import logger
from functools import wraps

from typer import Context

from pvgisprototype.constants import (
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
)
from pvgisprototype.core.hashing import generate_hash

logger.remove()


def initialize_logger(
    ctx: Context,
    log_level: None | int = None,
):
    """
    Initialise logging to either stderr or a file ?

    Notes
    -----
    Attention : Used in typer_option_log !

    """
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
        1: "INFO",  # Show info, warnings, and errors
        # Define more levels ?
        7: "DEBUG",  # Show debug messages
    }
    minimum_log_level = LOGURU_LEVELS.get(log_level, "WARNING")
    # print(f'Minimum log level : {minimum_log_level}')

    rich_handler = ctx.params.get("log_rich_handler")
    if rich_handler:
        print("RichHandler")
        logger.remove()
        import richuru

        richuru.install(level=0, rich_traceback=False)

    if log_level and not rich_handler:
        import sys
        # print(f"Logging to sys.stderr : {sys.stderr}")

        # logger.add(sys.stderr, enqueue=True, backtrace=True, diagnose=True)
        fmt = "{time} | {level: <8} | {name: ^15} | {function: ^15} | {line: >3} | {message}"
        logger.add(sys.stderr, format=fmt, level=minimum_log_level)
        logger.info(f"Logging to sys.stderr : {sys.stderr}")

    log_file = ctx.params.get("log_file")
    if log_file:
        if not rich_handler:
            logger.info(f"Logging to file : {log_file}")

        else:
            logger.info(
                f"Logging to file : {log_file}",
                alt=f"Logging to file : [reverse]{log_file}[/reverse] ?",
            )

        log_file = "pvgisprototype_{time}.log"
        logger.add(log_file, level=minimum_log_level)  # , compression="tar.gz")
        # logger.info(f'Logging to file : {log_file}', alt=f'Logging to file : [reverse]{log_file}[/reverse] ?')

    return log_level

def initialize_web_api_logger(log_level="INFO", use_rich=False):
    """
    Initialize Loguru logger for FastAPI and optionally enable Rich logging.
    
    Parameters:
        log_level (str): Log level (e.g., "DEBUG", "INFO").
        use_rich (bool): Whether to enable Rich for colorful logs.
    """
    import sys
    # Remove existing handlers to prevent duplicate logs
    logger.remove()

    # Define log format
    fmt = "{time} | {level: <8} | {name: ^15} | {function: ^15} | {line: >3} | {message}"

    # Add Loguru console logging
    logger.add(sys.stderr, format=fmt, level=log_level)

    # Optional: Enable Rich for better log formatting
    if use_rich:
        try:
            import richuru  # Rich wrapper for Loguru
            richuru.install(level=log_level, rich_traceback=True)
            logger.info("✅ Rich logging enabled")
        except ImportError:
            logger.warning("⚠️ Rich is not installed. Defaulting to Loguru.")

    
    # Intercept standard `logging` and send it to Loguru. This is for uvicorn
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            level = logger.level(record.levelname).name if record.levelname in logger._core.levels else "INFO"
            logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())

    # Replace standard loggers with Loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = [InterceptHandler()]

    logger.info("✅ Web API Logger initialized with Loguru")


def log_function_call(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        verbosity_level = kwargs.get("log", 0) or 0
        if verbosity_level > HASH_AFTER_THIS_VERBOSITY_LEVEL:
            data_type = kwargs.get("dtype", None)
            import inspect

            parent_frame = inspect.stack()[1]
            logger.info(
                f"> Call : {function.__name__}() from {parent_frame.function}() in {parent_frame.filename}:{parent_frame.lineno}, Requested : {data_type}",
                alt=f"> Call {function.__name__}() from [reverse]{parent_frame.function}()[/reverse] in {parent_frame.filename}:{parent_frame.lineno}, Requested : [reverse]{data_type}[/reverse]",
            )
        return function(*args, **kwargs)

        # if verbosity_level > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        #     logger.debug(f"Function {func.__name__} completed with locals: {locals()}")

    return wrapper


def log_data_fingerprint(
    data,
    log_level,
    hash_after_this_verbosity_level=2,
    output=None,
):
    """ """
    if output:
        print(type(output))
    if log_level > hash_after_this_verbosity_level:
        import inspect

        caller_name = inspect.stack()[1].function
        data_hash = generate_hash(data)
        logger.info(
            f"< Output {caller_name}() : {type(data)}, {data.dtype}, Hash {data_hash}",
            alt=f"< [bold]Output[/bold] of {caller_name}() : {type(data)}, [reverse]{data.dtype}[/reverse], Hash [code]{data_hash}[/code]",
        )
    if log_level > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        from devtools import debug

        debug(locals())

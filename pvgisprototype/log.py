"""
Attention : This should be part of the main() function, that is : a global
logging mechanism and configuration.
"""

import logging
from datetime import time, timedelta
from functools import wraps

from loguru import logger
from typer import Context

from pvgisprototype.constants import (
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
)
from pvgisprototype.core.hashing import generate_hash

WEB_SERVER_LOGGERS_LIST = [
    "uvicorn",
    "uvicorn.error",
    "uvicorn.access",
    "fastapi",
    "gunicorn",
    "gunicorn.access",
    "gunicorn.error",
    "gunicorn.http",
    "gunicorn.http.wsgi",
    "gunicorn.glogging",
]

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
        logger.debug(f"Logging to sys.stderr : {sys.stderr}")

    log_file = ctx.params.get("log_file")
    if log_file:
        if not rich_handler:
            logger.debug(f"Logging to file : {log_file}")

        else:
            logger.debug(
                f"Logging to file : {log_file}",
                alt=f"Logging to file : [reverse]{log_file}[/reverse] ?",
            )

        log_file = "pvgisprototype_{time}.log"
        logger.add(log_file, level=minimum_log_level)  # , compression="tar.gz")
        # logger.debug(f'Logging to file : {log_file}', alt=f'Logging to file : [reverse]{log_file}[/reverse] ?')

    return log_level


def redirect_web_server_logs(
    logger,
    web_server_loggers: str | list = WEB_SERVER_LOGGERS_LIST,
):
    """
    Redirects web server logs to Loguru and prevents duplicate handlers.

    Parameters
    ----------
    web_server_loggers : str | list, optional
        WSGI/ASGI server name loggers to redirect, by default WEB_SERVER_LOGGERS_LIST

    Notes
    -----

    *   This function is based on the example provided in Loguru documentation for
        redirecting web server logs.
    *   The function changes the handler for the specified loggers to intercept the logs
        and forward them to Loguru.
    *   It also prevents duplicate logs by setting the propagate attribute of the
        logger to False.
    """

    class InterceptHandler(logging.Handler):
        """
        Default handler from examples in loguru documentaion.
        See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
        """

        def emit(self, record: logging.LogRecord):
            # NOTE Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno  # type: ignore[assignment]

            logger.debug("> Getting logger: {}", record.name)

            # NOTE Preserve the original logger name (e.g. "uvicorn.access", "fastapi", etc.)
            logger.bind(name=record.name).opt(
                depth=6,  # NOTE Adjusts traceback depth to match real origin
                exception=record.exc_info,
            ).log(level, record.getMessage())

    logger.debug(
        "Replacing logger handlers!",
        alt="i [bold]Replacing logger handlers![/bold]",
    )

    for name in sorted(logging.root.manager.loggerDict.keys()):
        logger.debug("Discovered logger: {}", name)

    if type(web_server_loggers) is str:

        logger.debug(
            ">Trying to get all available loggers for server: {web_server_loggers},"
            "alt=>Trying to get all available loggers for server: [reverse]{web_server_loggers}[/reverse],"
        )

        loggers = (
            logging.getLogger(name)
            for name in logging.root.manager.loggerDict
            if name.startswith(f"{web_server_loggers}")
        )
    else:
        loggers = web_server_loggers  # type:ignore[assignment]

    logger.debug(
        f"Web server loggers: {loggers}",
        alt=f"Web server loggers: [reverse]{loggers}[/reverse]",
    )

    # NOTE Change handler for selected loggers
    for web_server_logger in loggers:
        logger.debug(
            f"Replacing handler for {web_server_logger}.",
            alt=f"Replacing handler for [reverse]{web_server_logger}[/reverse].",
        )
        logging.getLogger(f"{web_server_logger}").handlers = [InterceptHandler()]
        logging.getLogger(f"{web_server_logger}").propagate = (
            False  # NOTE Prevents duplicate logs
        )


def initialize_web_api_logger(
    log_level: str = "INFO",
    rich_handler: bool = False,
    server: str = "uvicorn",
    web_server_loggers: str | list = WEB_SERVER_LOGGERS_LIST,
    error_log_path: str | None = None,
    access_log_path: str | None = None,
    rotation: str | int | time | timedelta | None = None,
    retention: str | int | timedelta | None = None,
    compression: str | None = None,
    **kwargs,
):
    """
    Initialize Loguru logger for FastAPI and optionally enable Rich logging.

    This function configures a Loguru logger for FastAPI and Uvicorn (or any other
    web server) with the specified log level, format, and output targets.

    Parameters
    ----------
    log_level : str, optional
        Minimum log level to record, by default "INFO".
    rich_handler : bool, optional
        Enable Rich logging, by default False.
    server : str, optional
        Name of the web server to configure logs for, by default "uvicorn".
    web_server_loggers : str or list, optional
        Names of web server loggers to redirect to Loguru, by default
        WEB_SERVER_LOGGERS_LIST.
    format : str, optional
        Log format, by default "plain".
    error_log_path : str or None, optional
        Path to the error log file, by default "error.log".
    access_log_path : str or None, optional
        Path to the access log file, by default "access.log".
    rotation : str or int or time or timedelta or RotationFunction or None, optional
        Log rotation configuration, see https://loguru.readthedocs.io/en/stable/overview.html#easier-file-logging-with-rotation-retention-compression, by default None.
    **kwargs : dict
        Additional keyword arguments to pass to Loguru. See https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add

    Returns
    -------
    None
    """
    import sys

    # NOTE Remove existing handlers to prevent duplicate logs
    logger.remove()

    def format_record(record):
        request_id = record["extra"].get("request_id", "-")
        safe_message = record["message"].replace("{", "{{").replace("}", "}}")

        return (
            f"<green>{record['time']:YYYY-MM-DD HH:mm:ss}</green> | "
            f"<level><bold>{record['level'].name:<8}</bold></level> | "
            f"<magenta>{request_id}</magenta> | "
            f"<cyan>{record['name']}</cyan> | "
            f"<bold><level>{safe_message}</level></bold>\n"
        )

    def is_access_log(record):
        """
        Check if a log record is an access log.

        Parameters
        ----------
        record : dict
            Log record to check.

        Returns
        -------
        bool
            True if the log record is an access log, False otherwise.
        """
        name = record.get("extra", {}).get("name", "")
        if name == "pvgis.access":
            return True

        return False

    def is_error_log(record):
        """
        Check if a log record is an error log.

        Parameters
        ----------
        record : loguru.Record
            The log record to check.

        Returns
        -------
        bool
            True if the log record is an error log, False otherwise.
        """
        return not is_access_log(record)

    def exclude_server_logs(record, server="uvicorn"):
        """Ignore logs from Uvicorn's internal access logger."""
        return not (record["name"].startswith(server))

    logger.add(
        sys.stdout,
        colorize=True,
        format=format_record,
        filter=lambda record: (
            record["level"].no >= logger.level(log_level.upper()).no
            and record["level"].no < logging.WARNING
            and exclude_server_logs(record, server=server)
        ),
        enqueue=True,
    )

    # NOTE stderr: user level ≤ log and log ≥ WARNING
    logger.add(
        sys.stderr,
        colorize=True,
        format=format_record,
        filter=lambda record: (
            record["level"].no >= logger.level(log_level.upper()).no
            and record["level"].no >= logging.WARNING
            and exclude_server_logs(record, server=server)
        ),
        enqueue=True,
    )

    # NOTE Access log file
    if access_log_path:
        logger.add(
            access_log_path,
            level=log_level,
            format=format_record,
            filter=lambda record: (
                is_access_log(record) and exclude_server_logs(record, server=server)
            ),
            serialize=access_log_path.endswith(".json"),
            enqueue=True,
            rotation=rotation,
            retention=retention,
            compression=compression,
            **kwargs,
        )

    # NOTE Error log file
    if error_log_path:
        logger.add(
            error_log_path,
            level=log_level,
            format=format_record,
            filter=lambda record: (
                is_error_log(record) and exclude_server_logs(record, server=server)
            ),
            enqueue=True,
            serialize=error_log_path.endswith(".json"),
            rotation=rotation,
            retention=retention,
            compression=compression,
            **kwargs,
        )

    # NOTE Optional: Enable Rich for better log formatting
    if rich_handler:
        try:
            import richuru  # NOTE Rich wrapper for Loguru

            richuru.install(
                level=log_level,
                rich_traceback=True,
            )
            logger.debug(
                "i Rich logging enabled.",
                alt="i [bold]Rich[/bold] logging [green]enabled[/green].",
            )
        except ImportError:
            logger.warning(
                "⚠️ Rich is not installed. Defaulting to Loguru.",
                alt="i ⚠️ [bold]Rich is not installed[/bold]. Defaulting to Loguru.",
            )

    redirect_web_server_logs(logger, web_server_loggers=web_server_loggers)

    logger.debug(
        "i Web API Logger initialized with Loguru. ✅",
        alt="i [bold]Web API Logger[/bold] initialized [green]successfuly[/green] with [reverse][bold]Loguru[/bold][/reverse]. ✅",
    )


def log_function_call(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        verbosity_level = kwargs.get("log", 0) or 0
        if verbosity_level > HASH_AFTER_THIS_VERBOSITY_LEVEL:
            data_type = kwargs.get("dtype", None)
            import inspect

            parent_frame = inspect.stack()[1]
            logger.debug(
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
        logger.debug(
            f"< Output {caller_name}() : {type(data)}, {data.dtype}, Hash {data_hash}",
            alt=f"< [bold]Output[/bold] of {caller_name}() : {type(data)}, [reverse]{data.dtype}[/reverse], Hash [code]{data_hash}[/code]",
        )
    if log_level > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        from devtools import debug

        debug(locals())

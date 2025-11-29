#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
"""
# Unified Logger for PVGIS

This module provides a robust logging framework for functions in PVGIS.
It builds on top of Loguru and Rich logging,
supports advanced multi-environment configuration, logging to console, files,
or both and integrates popular web servers like Uvicorn, Gunicorn, and FastAPI.

## Features

- Central setup for Loguru and Rich logging
- Classic Python logging integration are supported
- Easy initialization of logging output and verbosity via Typer CLI Context
- Safe and consistent log message formatting by escaping curly braces.
- Web server logging redirection and duplicate prevention
- Readable logs in both CLI and web environments
- Functions, classes and decorators to facilitate tracing and data fingerprinting

## Usage

Typical use cases include command-line tools,
FastAPI web services requiring well-managed log output.
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


def _safe_message(message: str):
    """Escape curly braces in messages to prevent format parsing issues."""
    if isinstance(message, str):
        # If message contains '{}' but *no* extra args are supplied, neutralize them
        message = message.replace("{}", "{{}}")
        return message.replace("{", "{{").replace("}", "}}")


def _safe_log(func):
    """Decorator to securely format log messages for logger methods"""

    def wrapper(message, *args, **kwargs):
        return func(_safe_message(message), *args, **kwargs)

    return wrapper


from loguru import logger as _loguru_logger

for level in ("debug", "info", "warning", "error", "critical", "exception"):
    setattr(_loguru_logger, level, _safe_log(getattr(_loguru_logger, level)))

logger = _loguru_logger
logger.remove()


def suppress_noisy_loggers():
    """
    Suppress verbose log output from common third-party packages,
    i.e. matplotlib.
    """
    import logging

    logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)


def initialize_logger(
    ctx: Context,
    log_level: None | int = None,
):
    """
    Initialise logging via Typer's CLI context to either stderr or a file.

    Notes
    -----
    Attention : This function is used in `typer_option_log` !

    """
    suppress_noisy_loggers()

    LOGURU_LEVELS = {
        0: "WARNING",  # Only show warnings and errors
        1: "INFO",  # Show info, warnings, and errors
        # Define more levels ?
        7: "DEBUG",  # Show debug messages
    }
    minimum_log_level = LOGURU_LEVELS.get(log_level, "WARNING")

    rich_handler = ctx.params.get("log_rich_handler")
    if rich_handler:
        print("RichHandler")
        logger.remove()
        import richuru

        richuru.install(level=0, rich_traceback=False)

    if log_level and not rich_handler:
        import sys

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

    return log_level


def redirect_web_server_logs(
    logger,
    web_server_loggers: str | list = WEB_SERVER_LOGGERS_LIST,
):
    """
    Redirect web server logs to Loguru and prevent duplicate handlers.

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
        Handler to intercept and relay standard logging logs to Loguru.
        Default handler from examples in loguru documentaion.
        See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
        """

        def emit(self, record: logging.LogRecord):
            # NOTE Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno  # type: ignore[assignment]

            logger.debug(f"> Getting logger: {record.name}")

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
        logger.debug(f"Discovered logger: {name}")

    if type(web_server_loggers) is str:

        logger.debug(
            f">Trying to get all available loggers for server: {web_server_loggers},"
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
    log_console: bool = True,
    web_server_loggers: str | list = WEB_SERVER_LOGGERS_LIST,
    error_log_path: str | None = None,
    access_log_path: str | None = None,
    rotation: str | int | time | timedelta | None = None,
    retention: str | int | timedelta | None = None,
    compression: str | None = None,
    diagnose: bool = False,
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
    log_console : bool, optional
        Log to console, by default True.
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
    diagnose : bool, optional
        Enable diagnose mode, by default False.
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
        """
        Format structured log records for consistent appearance
        """
        request_id = record["extra"].get("request_id", "-")
        safe_message = record["message"]  # Already sanitized globally

        return (
            f"<green>{record['time']:YYYY-MM-DD HH:mm:ss}</green> | "
            f"<level><bold>{record['level'].name:<8}</bold></level> | "
            f"<magenta>{request_id}</magenta> | "
            f"<cyan>{record['name']}</cyan> | "
            f"<bold><level>{safe_message}</level></bold>\n"
        )

    def is_access_log(record) -> bool:
        """
        Check if a log record originates from the PVGIS access logger.

        This function identifies logs that have been tagged with the
        'pvgis.access' name in their extra metadata, typically used to
        distinguish API access logs from other application logs.

        Parameters
        ----------
        record : dict
            Loguru log record to check.

        Returns
        -------
        bool
            True if the record is tagged with name 'pvgis.access', False otherwise.
        """
        name = record.get("extra", {}).get("name", "")
        if name == "pvgis.access":
            return True

        return False

    def is_error_log(record) -> bool:
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

    if log_console:
        logger.add(
            sys.stdout,
            colorize=True,
            format=format_record,
            filter=lambda record: (
                record["level"].no >= logger.level(log_level.upper()).no
                and record["level"].no < logging.WARNING
                and exclude_server_logs(record, server=server)
            ),
            diagnose=diagnose,
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
            diagnose=diagnose,
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
            rotation=rotation,
            retention=retention,
            compression=compression,
            diagnose=diagnose,
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
            serialize=error_log_path.endswith(".json"),
            rotation=rotation,
            retention=retention,
            compression=compression,
            diagnose=diagnose,
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
    """Decorator to log function calls and verbosity"""

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

    return wrapper


def log_data_fingerprint(
    data,
    log_level,
    hash_after_this_verbosity_level=2,
    output=None,
):
    """Log a fingerprint and optionally a hash of data objects for traceability."""
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

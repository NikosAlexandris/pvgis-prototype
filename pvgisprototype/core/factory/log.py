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
Set FACTORY_LOG_FILE before running a script that uses this logger to log out
everything to a file !

"""
from typing import Dict, List
from loguru import logger
import sys
import os
from pathlib import Path
import yaml


# Configuration
LOG_LEVEL = os.getenv("FACTORY_LOG_LEVEL", "WARNING").upper()
LOG_FILE = os.getenv("FACTORY_LOG_FILE")
RICH_HANDLER = os.getenv("FACTORY_RICH", "true").lower() == "true"

LOG_FORMAT = "{time:HH:mm:ss} | {level: <7} | {name}:{line} | {message}"


def setup_factory_logger(
    verbose: bool = False,
    level: str = "WARNING",
    format: str = LOG_FORMAT,
    file: str | Path | None = None,
    rich_handler: bool = False,
):
    """
    Set up a clean logger for the definition factory.

    Parameters
    ----------
    verbose : (bool)
        If True, sets the logging level to DEBUG and shows logs in the console.
    
    level: str
        Log level

    file : str | Path | None
        The file path to log to. If None, logging will be to console.
    
    rich_handler : bool
        If True, enables rich formatting for console output.
    """
    logger.remove()  # Remove any existing handlers

    if rich_handler:
        import richuru
        richuru.install(level=level, rich_traceback=True)
        logger.debug(f"Installed richuru")

    level = 'DEBUG' if verbose else level
    if verbose:
        logger.debug(
            "Logging directed to `sys.stderr`",
            alt=f"Logging directed to `sys.stderr`",
        )
        logger.add(
            sink=sys.stderr,
            level=level,
            format=format,
            backtrace=False,
            diagnose=False,
        )

    if file:
        logger.info(
            "Logging to file {file}",
            file=file,
            alt=f"Logging to file {file}",
        )
        logger.add(
                sink=file,
                level=level,
                format=format,
                backtrace=True,
                diagnose=True,
        )

    logger.info("Factory logger initialized")


def log_node(
    node_type: str,
    key: str | int,
    value: Dict | List | None = None,
    state_message: str | None = '',
    message_style: str | None = '',
    ):
    """
    """
    message_style_open = f"[{message_style}]" if message_style else ''
    message_style_close = f"[/{message_style}]" if message_style else ''
    value_type = '| ' + str(type(value)) if value else ''
    value = f"\n\n   {value}\n" if value else ''

    logger.debug(
        "{node_type} key {key} {state_message} {value_type} {value}",
        node_type=node_type,
        key=key,
        state_message=state_message,
        value_type=value_type,
        value=value,
        alt=f"[dim]{node_type} key[/dim] [bold]{key}[/bold] {message_style_open}{state_message}{message_style_close} [bold]{value_type}[/bold] {value}",
    )


def log_action(
    action: str,
    action_style: str,
    object_name: str,
    details: str | None = None,
):
    """
    """
    action_style = 'dim' + f' {action_style}'
    details = f"\n\n{details=}\n"
    logger.info(
        "{action} {object_name} {details}",
        action=action,
        object_name=object_name,
        details=details,
        # extra={'object_name': data_model_name, 'details': details},
        alt=f"[{action_style}]{action}[/{action_style}] [bold]{object_name=}[/bold]{details}"
    )


def log_data_model_loading(
        data_model,
        data_model_name,
        require: bool = False,
        ):
    """
    """
    if not require:
        logger.debug(
            "Processing data model {data_model_name}",
            data_model_name=data_model_name,
            alt=f"[dim]Processing data model [code]{data_model_name}[/code] :[/dim]\n\n{yaml.dump(data_model, sort_keys=False)}",
        )
    else:
        logger.debug(
             "Require data model :\n{yaml.dump(data_model, default_flow_style=False, sort_keys=False,)}",
             data_model=data_model,
             alt=f"Require data model :\n[bold]{yaml.dump(data_model, default_flow_style=False, sort_keys=False,)}[/bold]"
        )

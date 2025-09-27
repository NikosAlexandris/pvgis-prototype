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
import typer

from pvgisprototype.log import initialize_logger

typer_option_log = typer.Option(
    "--log",
    "-l",
    help="Enable logging",
    # help="Specify a log file to write logs to, or omit for stderr.")] = None,
    count=True,
    is_flag=False,
    callback=initialize_logger,
    # default_factory=0,
)
typer_option_log_rich_handler = typer.Option(
    "--log-rich-handler",
    "--log-rich",
    help="Use RichHandler along with `--log` to prettify logs",
    # default_factory=False,
)
typer_option_logfile = typer.Option(
    "--log-file",
    help="Optional log file",
    # default_factory=False,
)

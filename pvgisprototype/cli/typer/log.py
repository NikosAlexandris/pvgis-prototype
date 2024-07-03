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

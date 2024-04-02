import typer
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_output


typer_option_verbose = typer.Option(
    '--verbose',
    '-v',
    help='Show details while executing commands',
    count=True,
    is_flag=False,
    show_default=True,
    rich_help_panel=rich_help_panel_output,
)
typer_option_quiet = typer.Option(
    '--quiet',
    help='Do not print out the output',
    is_flag=True,
    show_default=True,
    rich_help_panel=rich_help_panel_output,
)


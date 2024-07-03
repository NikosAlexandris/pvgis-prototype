import typer

from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_output


def callback_analysis_of_performance(
    ctx: typer.Context,
    verbose: int,
):
    """Callback function : set verbose to >=7 if analysis is requested !"""
    analysis = ctx.params.get("analysis")
    quick_response_code = ctx.params.get("quick_response_code")
    if analysis or quick_response_code:
        if verbose < 7:
            verbose = 9
    return verbose


def callback_quiet(
    ctx: typer.Context,
    quiet: bool,
) -> bool:
    """ """
    analysis = ctx.params.get("analysis")
    if analysis and not quiet:
        quiet = True
    return quiet


typer_option_verbose = typer.Option(
    "--verbose",
    "-v",
    help="Show details while executing commands",
    rich_help_panel=rich_help_panel_output,
    count=True,
    is_flag=False,
    show_default=True,
    callback=callback_analysis_of_performance,
)
typer_option_quiet = typer.Option(
    "--quiet",
    help="Do not print out the output",
    is_flag=True,
    show_default=True,
    rich_help_panel=rich_help_panel_output,
    callback=callback_quiet,
)

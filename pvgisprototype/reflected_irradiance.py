import typer


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Calculate reflected solar irradiance",
)


@app.command('reflected', no_args_is_help=True)
def calculate_reflected_irradiance():
    """
    """
    pass


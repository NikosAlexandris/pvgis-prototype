import typer


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Calculate diffuse solar irradiance",
)


@app.command('diffuse', no_args_is_help=True)
def calculate_diffuse_irradiance():
    """
    """
    pass


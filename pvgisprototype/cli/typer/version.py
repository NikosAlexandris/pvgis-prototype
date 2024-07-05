"""
Version parameters
"""

import typer


def _version_callback(flag: bool) -> None:
    if flag:
        from pvgisprototype._version import __version__

        print(f"PVGIS prototype version: {__version__}")
        raise typer.Exit(code=0)


typer_option_version = typer.Option(
    "--version",
    help="Show the version of the application and exit",
    callback=_version_callback,
    is_eager=True,
    # default_factory=None,
)

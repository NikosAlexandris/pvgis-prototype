import typer
from pathlib import Path


def validate_path(path: Path) -> Path:
    """Validate the path according to custom constraints."""
    if not path.exists():
        raise typer.BadParameter("Path does not exist.")
    if not path.is_file():
        raise typer.BadParameter("Path is not a file.")
    # if not path.is_readable():
    #     raise typer.BadParameter("File is not readable.")
    return path.resolve()

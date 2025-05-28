from pathlib import Path
from typing import Dict, Any, List
from pvgisprototype.core.factory.definition.consolidate import load_data_model
from rich.table import Table
from rich.progress import track
from rich.console import Console
from pvgisprototype.core.factory.log import logger


def build_python_data_models(source_path: Path, yaml_files: List[str], verbose: bool = False) -> Dict[str, Any]:
    """Aggregate multiple PVGIS-native data models into a single dictionary."""
    logger.info(
            "Building PVGIS-native Python data models",
            alt=f"Building PVGIS-native Python data models"
    )
    data_models = {}
    logger.debug(
            "PVGIS bases upon a series of native data models. "
            + "These are defined in YAML files located in the directory {source_path}."
            + "\n",
            source_path=source_path,
        alt=(
            f"[bold]PVGIS bases upon a series of native data models. [/bold]"
            + f"These are defined in YAML files located in the directory [code]{source_path}[/code]."
            + f"\n"
        )
    )
    logger.info(
        f"Reading YAML definitions in {source_path}",
        alt=f"[bold]Reading[/bold] YAML definitions in [code]{source_path}[/code]"
    )

    table = Table(box=None, show_header=False, show_edge=False, pad_edge=False)

    for yaml_file in track(yaml_files, description="Building data models...\n"):
        full_yaml_path = source_path / yaml_file
        data_model = load_data_model(source_path, full_yaml_path)
        table.add_row(f"- {next(iter(data_model))}")
        data_models.update(data_model)

    if verbose:
        Console().print(table)
        Console().print()

    return data_models

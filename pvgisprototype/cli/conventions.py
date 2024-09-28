from rich import print
from pvgisprototype.api.conventions import generate_pvgis_conventions


def print_pvgis_conventions() -> None:
    print(generate_pvgis_conventions())


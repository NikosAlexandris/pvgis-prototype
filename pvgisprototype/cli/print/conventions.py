from rich import print
from pvgisprototype.api.conventions import (
    ASSUMPTIONS_FOR_INPUT_DATA_IN_PVGIS,
    PHOTOVOLTAIC_EFFIENCY_COEFFICIENTS,
    SOLAR_INCIDENCE_ANGLE,
    TIME_IN_PVGIS,
    UNITS_IN_PVGIS,
    generate_pvgis_conventions,
)


def print_pvgis_conventions() -> None:
    print(
        generate_pvgis_conventions(),
        generate_pvgis_conventions(UNITS_IN_PVGIS),
        generate_pvgis_conventions(TIME_IN_PVGIS),
        generate_pvgis_conventions(ASSUMPTIONS_FOR_INPUT_DATA_IN_PVGIS),
        generate_pvgis_conventions(SOLAR_INCIDENCE_ANGLE),
        generate_pvgis_conventions(PHOTOVOLTAIC_EFFIENCY_COEFFICIENTS),
    )

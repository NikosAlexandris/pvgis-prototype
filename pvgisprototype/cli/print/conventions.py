#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
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

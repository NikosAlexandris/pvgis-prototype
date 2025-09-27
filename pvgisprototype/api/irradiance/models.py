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
from enum import Enum


class DirectIrradianceComponents(str, Enum):
    normal = "normal"
    on_horizontal_surface = "horizontal"
    on_inclined_surface = "inclined"


class MethodForInexactMatches(str, Enum):
    none = None  # only exact matches
    pad = "pad"  # ffill: propagate last valid index value forward
    backfill = "backfill"  # bfill: propagate next valid index value backward
    nearest = "nearest"  # use nearest valid index value


class SolarPanelTechnology(str, Enum):
    none = None
    cSi = "cSi"
    old_cSi = "Old cSi"
    CIS = "CIS"
    CdTe = "CdTe"


class ModuleTemperatureAlgorithm(str, Enum):
    none = None
    faiman = "Faiman"

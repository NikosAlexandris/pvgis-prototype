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
"""
definitions.yaml
----------------------------------

The `definitions.yaml` YAML directory contains the definition of
custom _atomic_ data classes required by `pvgisprototype`'s application
programming interface (API) and, hence, subsequently by the command line
interface (CLI) and the Web API components.  Atomic data classes are used then
to build more complex data structures defined in `parameters.py` (or let's call
them Models) using Pydantic to serve input data validation purposes and more.

The content is parsed and converted into a native Python dictionary at
installation time.  ::: FIXME -- ToDo ! :::


Custom data classes
-------------------

The definition of a custom data class includes type, initial values, units, and
a textual description. The content is organized in sections : 'Where?',
  'When?', 'Atmospheric properties', 'Earth orbit' and more.

Each custom data class is described by the following (nested) key-value pairs:

    - value       : 'type' of and 'initial' value
    - unit        : 'type' of and 'initial' value
    - symbol      : used to visually distinguish a parameter
    - description : textual description of the parameter supported by the class


See Also
--------

- Python's PyYAML library for YAML file parsing:
  https://pypi.org/project/PyYAML/


Examples
--------

- Longitude:
    value:
        type: float | None
        initial:
    unit:
        type: str | None
        initial:
    symbol: Λ
    description: "The angle between a point on the Earth's surface and the meridian plane, ranging from 0° at the Prime Meridian to 180° east or west."
"""

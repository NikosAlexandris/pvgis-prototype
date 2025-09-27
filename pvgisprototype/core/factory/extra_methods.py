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
from pvgisprototype.core.factory.context import populate_context


def to_dictionary(self):
    return {
        field: getattr(self, field)
        for field in self.__annotations__
        if hasattr(self, field)
    }


def build_output(self, verbose: int = 0, fingerprint: bool = False):
    return populate_context(self, verbose, fingerprint)


EXTRA_METHODS = {
    "to_dictionary": to_dictionary,
    "build_output": build_output,
}

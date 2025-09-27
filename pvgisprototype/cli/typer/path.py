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
from pathlib import Path

import typer


def validate_path(path: Path) -> Path:
    """Validate the path according to custom constraints."""
    if not path.exists():
        raise typer.BadParameter("Path does not exist.")
    # if not path.is_file():
    #     raise typer.BadParameter("Path is not a file.")
    # if not path.is_readable():
    #     raise typer.BadParameter("File is not readable.")
    return path.resolve()

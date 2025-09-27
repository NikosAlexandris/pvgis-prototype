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
from typing import Annotated
import typer
from rich import print
from pvgisprototype.api.citation import generate_citation_text


def print_citation_text(
    bibtex: Annotated[bool, typer.Option(help="Print citation in BibTeX format.")] = False,
) -> None:
    """
    """
    citation = generate_citation_text(bibtex=bibtex)
    print(citation)

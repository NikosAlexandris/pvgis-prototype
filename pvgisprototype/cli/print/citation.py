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

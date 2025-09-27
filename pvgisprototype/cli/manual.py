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
from typing import Annotated

import typer
import yaml

SOLAR_RADIATION_DICTIONARY_YAML_FILE = "data/variables.yml"


app = typer.Typer(
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=":book: Manual for solar radiation terms",
)


def read_yaml_file(file_path: str):
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
    return data


def get_lemma(data, lemma_name: str):
    for item in data:
        if item["lemma"] == lemma_name:
            return item
    return None


def wrap_text(text, max_words=8):
    words = text.split()
    wrapped_text = "\n".join(
        " ".join(words[i : i + max_words]) for i in range(0, len(words), max_words)
    )
    return wrapped_text


@app.command("info", no_args_is_help=True, help="Info")
def read_lemma(
    lemma_name: str = typer.Argument(None),
    file_path: str = SOLAR_RADIATION_DICTIONARY_YAML_FILE,
    maximum_words_in_description_rows: int = 10,
):
    data = read_yaml_file(file_path)

    if lemma_name:
        lemma = get_lemma(data, lemma_name)
        if lemma:
            from rich.box import SIMPLE
            from rich.console import Console
            from rich.table import Table

            table = Table(show_header=True, box=SIMPLE, header_style="bold magenta")
            table.add_column("Field", style="dim", width=20)
            table.add_column("Value", min_width=20)
            table.add_row("Lemma", lemma["lemma"])
            table.add_row("Lemma name in Python", lemma["lemma_name"])
            table.add_row("Symbol", lemma["symbol"])
            table.add_row(
                "Description",
                wrap_text(lemma["description"], maximum_words_in_description_rows),
            )
            table.add_row("Units", lemma["units"])
            table.add_row("Tags", ", ".join(lemma["tags"]))
            Console().print(table)
        else:
            typer.echo(f"Lemma '{lemma_name}' not found.")
    else:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Lemma", style="dim", width=20)
        table.add_column("Symbol", min_width=20)
        table.add_column("Description")
        table.add_column("Units")
        table.add_column("Tags")
        for item in data:
            table.add_row(
                item["lemma"],
                item["symbol"],
                wrap_text(item["description"], maximum_words_in_description_rows),
                item["units"],
                ", ".join(item["tags"]),
            )
            Console().print(table)


@app.command("update", no_args_is_help=True, help="Update")
def update_solar_radiation_dictionary(
    lemma: Annotated[str, typer.Argument(help="Lemma")],
    lemma_name: Annotated[str, typer.Argument(help="lemma_name (snake_case)")],
    symbol: Annotated[str, typer.Argument(help="Symbol for Lemma")],
    description: Annotated[str, typer.Argument(help="Description of Lemma")],
    units: Annotated[str, typer.Argument(help="Units for Lemma")],
    tags: Annotated[str, typer.Argument(help="Tags for Lemma (comma-separated)")],
    dictionary_yaml_file: Annotated[
        Path, typer.Option(help="Path to the dictionary YAML file")
    ] = Path(".data/solar_radiation_dictionary.yml"),
):
    """
    Examples
    --------
    pvis manual update "lemma-name" lemma_name "Symbol" "Description" "Units" "tag1, tag2, tag3"
    """
    tags_list = [tag.strip() for tag in tags.split(",")]

    new_entry = {
        "lemma": lemma,
        "lemma_name": lemma_name,
        "symbol": symbol,
        "description": description,
        "units": units,
        "tags": tags_list,
    }

    with open(dictionary_yaml_file, "r") as file:
        data = yaml.safe_load(file)

    existing_lemma = next((v for v in data if v["lemma_name"] == lemma_name), None)

    if existing_lemma:
        existing_lemma.update(new_entry)
        typer.echo(f"Updated existing lemma: {lemma_name}")
    else:
        data.append(new_entry)
        typer.echo(f"Added new lemma: {lemma_name}")

    with open(dictionary_yaml_file, "w") as file:
        yaml.dump(data, file)


if __name__ == "__main__":
    app()

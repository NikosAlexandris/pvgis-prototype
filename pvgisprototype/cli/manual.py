import typer
from typing import Annotated
from typing import Optional
import yaml
from pathlib import Path


app = typer.Typer(
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=':book:  Manual for solar radiation variables',
)


def read_yaml(file_path: str):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data


def get_variable(data, variable_name: str):
    for item in data:
        if item['variable'] == variable_name:
            return item
    return None


@app.command('info', no_args_is_help=True, help='Info')
def read_variable(file_path: str, variable_name: str = typer.Argument(None)):
    data = read_yaml(file_path)
    
    if variable_name:
        variable = get_variable(data, variable_name)
        if variable:
            typer.echo(f"Variable: {variable['variable']}")
            typer.echo(f"Variable name in Python: {variable['variable_name']}")
            typer.echo(f"Symbol: {variable['symbol']}")
            typer.echo(f"Description: {variable['description']}")
            typer.echo(f"Units: {variable['units']}")
            typer.echo(f"Tags: {variable['tags']}")
            typer.echo()
        else:
            typer.echo(f"Variable '{variable_name}' not found.")
    else:
        for item in data:
            typer.echo(f"Variable: {item['variable']}")
            typer.echo(f"Symbol: {item['symbol']}")
            typer.echo(f"Description: {item['description']}")
            typer.echo(f"Units: {item['units']}")
            typer.echo(f"Tags: {item['tags']}")
            typer.echo()


@app.command('update', no_args_is_help=True, help='Update')
def update_variables_file(
        variable: Annotated[str, typer.Argument(help='Variable name')],
        variable_name: Annotated[str, typer.Argument(help='Variable name (snake_case)')],
        symbol: Annotated[str, typer.Argument(help='Variable symbol')],
        description: Annotated[str, typer.Argument(help='Variable description')],
        units: Annotated[str, typer.Argument(help='Variable units')],
        tags: Annotated[str, typer.Argument(help='Variable tags (comma-separated)')],
        variables_file: Annotated[Path, typer.Option(help='Path to the variables YAML file')] = Path('.data/variables.yml'),
        ):
    """
    Examples
    --------
    pvis manual update "Variable Name" variable_name "Symbol" "Description" "Units" "tag1, tag2, tag3"
    """
    tags_list = [tag.strip() for tag in tags.split(',')]

    new_entry = {
        'variable': variable,
        'variable_name': variable_name,
        'symbol': symbol,
        'description': description,
        'units': units,
        'tags': tags_list
    }

    with open(variables_file, 'r') as file:
        data = yaml.safe_load(file)

    existing_variable = next((v for v in data if v['variable_name'] == variable_name), None)

    if existing_variable:
        existing_variable.update(new_entry)
        typer.echo(f"Updated existing variable: {variable_name}")
    else:
        data.append(new_entry)
        typer.echo(f"Added new variable: {variable_name}")

    with open(variables_file, 'w') as file:
        yaml.dump(data, file)


if __name__ == '__main__':
    app()

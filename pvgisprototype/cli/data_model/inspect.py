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
from typing import Annotated, Any
from pvgisprototype.core.factory.definition.load import load_yaml_file
from pvgisprototype.core.factory.log import setup_factory_logger, logger
import typer
import yaml


import os
LOG_LEVEL = os.getenv("FACTORY_LOG_LEVEL", "WARNING").upper()
LOG_FILE = os.getenv("FACTORY_LOG_FILE")
RICH_HANDLER = os.getenv("FACTORY_RICH", "true").lower() == "true"


def load_python_module(module_path: Path) -> Any:
    """Dynamically load a Python module from a file path."""
    module_name = module_path.stem
    spec = util.spec_from_file_location(module_name, module_path)
    if spec is None:
        raise ImportError(f"Could not load module from {module_path}")
    
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def inspect_yaml_definition(
    yaml_file: Path,
    verbose: Annotated[bool, typer.Option(help="Verbose")] = False,
    log_file: Annotated[
        str | None, typer.Option("--log-file", "-l", help="Log file")
    ] = LOG_FILE,
    log_level: str = LOG_LEVEL,
    rich_handler: Annotated[
        bool, typer.Option("--rich", "--no-rich", help="Rich handler")
    ] = RICH_HANDLER,
):
    """ """
    # Initialize logging
    setup_factory_logger(
        verbose=verbose,
        level=log_level,
        file=log_file,
        rich_handler=rich_handler,
    )

    print(
            yaml.dump(
                load_yaml_file(yaml_file),
                sort_keys=False,
            )
        )


def inspect_python_definition(
    python_module: Path,
    definition: str = "Fingerprint",  # The key to look for in the module's dictionary
    attribute: str | None = None,
    verbose: Annotated[bool, typer.Option(help="Verbose")] = False,
    log_file: Annotated[
        str | None, typer.Option("--log-file", "-l", help="Log file")
    ] = LOG_FILE,
    log_level: str = LOG_LEVEL,
    rich_handler: Annotated[
        bool, typer.Option("--rich", "--no-rich", help="Rich handler")
    ] = RICH_HANDLER,
):
    """Inspect a specific dictionary key from a Python module."""
    
    # Initialize logging
    setup_factory_logger(
        verbose=verbose,
        level=log_level,
        file=log_file,
        rich_handler=rich_handler,
    )

    if not definition:
        print(f"List all top-level data model definition names")

    else:
        try:
            # Load the data model definitions Python dictionary
            module = load_python_module(python_module)
            definitions = module.PVGIS_DATA_MODEL_DEFINITIONS
            
            # Extract the specific data model
            if definition in definitions:
                output = definitions[definition]

                if attribute and attribute in output:
                    output = definitions[definition][attribute]
                
                # Print in YAML format for consistent visualization
                print(
                    yaml.dump(
                        data=output,
                        sort_keys=False,
                        default_flow_style=False,
                        indent=2
                    )
                )
            else:
                logger.warning(f"Key '{definition_key}' not found in the definitions dictionary.")
                raise typer.Exit(code=1)
                
        except AttributeError:
            typer.echo("The module does not have a 'PVGIS_DATA_MODEL_DEFINITIONS' variable.")
            raise typer.Exit(code=1)

        except Exception as e:
            typer.echo(f"Error: {str(e)}")
            raise typer.Exit(code=1)


def inspect_pvgis_data_model(
    data_model: str = 'all',
):
    """
    """
    pass

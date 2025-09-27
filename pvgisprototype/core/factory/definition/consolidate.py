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
from typing import Dict, Any
from pathlib import Path
from typing import Any, Dict
from pvgisprototype.core.factory.definition.inheritance import resolve_requires
from pvgisprototype.core.factory.definition.load import load_yaml_file
from pvgisprototype.core.factory.log import logger, log_data_model_loading


def finalize_output(data: dict) -> dict:
    """Ensure output dict has required keys"""
    output = data.get('sections', {}).get('output', {})
    if isinstance(output, dict):
        output.setdefault('type', 'dict')
        output.setdefault('initial', {})
    return data


def load_data_model(
    source_path: Path,
    data_model_yaml: Path,
    require: bool = False,
) -> Dict[str, Any]:
    """
    Load and consolidate a YAML data model definition and return a nested
    dictionary compatible with `DataModelFactory`.
    """
    # Load data model description
    data_model = load_yaml_file(data_model_yaml)
    data_model_name = data_model.get('name', '<unnamed data model>')
    if data_model_name == '<unnamed data model>':
        logger.warning(f"The data model {data_model} lacks a 'name' key!")

    log_data_model_loading(
        data_model=data_model,
        data_model_name=data_model_name,
        require=require,
    )

    # Resolve requirements
    data_model = resolve_requires(
        data=data_model,
        source_path=source_path,
    )
    finalize_output(data=data_model)

    # del(data_model['sections']['_file_path'])  # sane post-processing ?

    # logger.info(
    #     "Return consolidated data model :\n" + yaml.dump(data={data_model_name: data_model['sections']}, default_flow_style=False, sort_keys=False),
    #     alt="[dim]Return consolidated data model :[/dim]\n" + yaml.dump(data={data_model_name: data_model['sections']}, default_flow_style=False, sort_keys=False),
    # )

    # Return the consolidated data model
    return {data_model_name: data_model.get('sections', {})}

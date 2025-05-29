import yaml
from typing import Dict, List, Union
from pvgisprototype.core.factory.log import logger


def find_structure_in_path(
    data: Dict,
    path: List[str],
) -> Union[List, None]:
    """
    Navigate nested dict to find structure at specified path.
    """
    data_model_name = data.get("name", "<unnamed data model>")
    if data_model_name == "<unnamed data model>":
        logger.warning(f"The data structure {data} lacks a 'name' key!")

    for part in path:
        if isinstance(data, dict) and part in data:
            data = data[part]
            logger.debug(
                "   Override output structure in {data_model_name} [Child]\n\n   {data}\n",
                data_model_name=data_model_name,
                data=data,
                alt=f"   [dim bold]Override output structure[/dim bold] in {data_model_name} [Child]\n\n   [dim]{data}[/dim]\n",
            )

        else:
            return None

    return data if isinstance(data, list) else None


def get_structure(data: Dict) -> List:
    """
    Retrieve the structure from the nested dictionary.
    If it doesn't exist, return an empty list.
    """
    output_structure = data.get("sections", {}).get("output", {}).get("structure", [])
    data_model_name = data.get('name', '<unnamed data structure>')
    if output_structure:
        yaml_dump_of_structure = yaml.dump(data=output_structure, sort_keys=False)
        logger.debug(
            "   Child node output structure"
            + " in {data_model_name} :"
            + "\n\n   {yaml_dump_of_structure}\n",
            data_model_name=data_model_name,
            yaml_dump_of_structure=yaml_dump_of_structure,
            alt=f"   [dim][bold]Child node[/bold] output structure[/dim]"
            + f" in {data_model_name} :"
            + f"\n\n   [dim]{yaml_dump_of_structure}[/dim]\n"
        )
    else:
        logger.debug(
            "   Child node"
            + " in `{data_model_name}` has no output structure !",
            data_model_name=data_model_name,
            alt=f"   [dim][bold]Child node[/bold][/dim]"
            + f" in {data_model_name} has no output structure !"
        )

    logger.debug(
        f"Returning child node\n\n{data=}\n\noutput structure is\n\n{output_structure=}"
    )

    return output_structure


def extract_structure_from_required(
    required_data: dict,
) -> List[dict]:
    """
    Extract the output structure list from the required file at
    `sections.output.structure`.
    """
    structure = []
    if 'sections' in required_data:
        output = required_data['sections'].get('output', {})
        if output:
            logger.debug(
                    f"   ! Identified an `output` structure !\n",
                    alt=f"   ! [blue bold]Identified an `output` structure ![/blue bold]\n",
                    )
        if 'structure' in output:
            structure = output['structure']
            required_data_model_name = required_data['name']
            yaml_dump_of_structure = yaml.dump(data=structure, sort_keys=False)
            logger.debug(
                "   Base output structure"
                + " in {required_data_model_name} :"
                + "\n\n   {yaml_dump_of_structure}\n",
                required_data_model_name=required_data_model_name,
                yaml_dump_of_structure=yaml_dump_of_structure,
                alt=f"   [dim][bold]Base[/bold] output structure[/dim]"
                + f" in {required_data_model_name} :"
                + f"\n\n   [dim]{yaml_dump_of_structure}[/dim]\n"
            )

    return structure



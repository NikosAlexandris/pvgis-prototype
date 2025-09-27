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
from typing import Any, Dict
from typing import List, Dict, Any
from copy import deepcopy
from pvgisprototype.core.factory.log import log_action, log_node, logger
import yaml


def merge_lists(
    base_list: List,
    override_list: List,
) -> List:
    """
    Merges two lists, ensuring no duplicates.
    If items are dicts, uses `section`, `name`, or `id` for deduplication.
    """
    log_action(
        action="/ Merging `override` list into `base`",
        action_style='',
        object_name='a pair of Lists',
        details="[Parent data model]",
    )

    # if base_list is None:
    #     return deepcopy(override_list) if override_list else []

    # if override_list is None:
    #     return base_list

    # merged = deepcopy(base_list)
    merged = base_list.copy()

    for item in reversed(override_list):

        if isinstance(item, dict):
            match_key = next((identifier for identifier in ("section", "name", "id") if identifier in item), None)

            if match_key:
                match = next((key for key in merged if isinstance(key, dict) and key.get(match_key) == item.get(match_key)), None)

                if match:
                    merged[merged.index(match)] = merge_dictionaries(base=match, override=item)

                else:
                    merged.append(item)

            elif item not in merged:
                merged.append(item)

        elif item not in merged:
            merged.append(item)
    
    yaml_dump_of_merged = yaml.dump(data=merged, sort_keys=False)
    log_action(
            action=f"Return merge list",
            action_style='underline',
            object_name='',
            details=yaml_dump_of_merged,
            )

    return merged


def merge_dictionaries(
    base: Dict[str, Any] | List[Any] | Any,
    override: Dict[str, Any] | None,
) -> Dict[str, Any]:
    """
    Recursively merge two dictionaries.
    Values in `override` will overwrite those in `base` if keys match.
    """
    logger.info(
        "Input data is\n\n{base}\n\nand\n\n{override}\n",
        base=base,
        override=override,
        alt=f"[code]Input data is[/code]\n\n{base=}\n\nand\n\n{override=}\n",
    )

    # if "name" in base and not isinstance(base["name"], dict):
    #     base_data_model_name = base["name"]
    #     # logger.debug(
    #     #     "/ Processing {base_data_model_name} [Parent]",
    #     #     base_data_model_name=base_data_model_name,
    #     #     alt=f"[dim]/ Processing [bold]{base_data_model_name}[/bold] [Parent][/dim]",
    #     # )
    #     log_action(
    #         action="/ Processing",
    #         action_style="",
    #         object_name=base_data_model_name,
    #         details="[Parent data model]",
    #     )

    if override is None:
        logger.info(
                "Override is None, returning the base dictionary!",
                alt="[orange]Override is None, returning the base dictionary![/orange]"
                )
        return base if base else {}

    if isinstance(base, dict):
        logger.debug(
            "Merging dictionaries",
            alt=f"[dim]Merging[/dim] {base.get('name', '<unnamed base>')} → {override.get('name', '<unnamed override>')}"
        )

    merged = deepcopy(base) if isinstance(base, (dict, list)) else base
    # merged = base.copy() if isinstance(base, (dict, list)) else base

    for override_key, override_value in override.items():
        log_node(
                node_type='Child',
                key=override_key,
                value=override_value,
        )

        # ----------------------------------------------
        if (
            override_value
            and isinstance(override_value, dict)
            and "name" in override_value
            and not isinstance(override_value['name'], dict)
        ):
            override_value_name = override_value["name"]
        else:
            override_value_name = ''
        # ----------------------------------------------

        if override_key in merged:
            base_value = merged[override_key]
            log_node(
                node_type='Child',  # the child key actually
                key=override_key,
                value=base_value,
                state_message="exists in Parent [will inherit]",
            )

            # ----------------------------------------------
            if (
                base_value
                and isinstance(base_value, dict)
                and "name" in base_value
                and not isinstance(base_value['name'], dict)
            ):
                base_value_name = base_value["name"]
            else:
                base_value_name = '<unnamed base value>'
            # ----------------------------------------------

            if isinstance(override_value, dict) and isinstance(base_value, dict):

                yaml_dump_of_merged = yaml.dump(data=merged, sort_keys=False)
                log_action(
                    action="Before merging dictionaries",
                    action_style="dim yellow",
                    object_name=f"{base_value_name}, {override_value_name}",
                    details=yaml_dump_of_merged,
                )

                try:
                    # Recursively merge nested dictionaries
                    merged[override_key] = merge_dictionaries(
                        base=base_value,
                        override=override_value,
                    )
                except Exception as exception:
                    logger.error(
                        "Error merging dictionaries for key `{override_key}` : {exception}",
                        override_key=override_key,
                        exception=exception,
                        alt=f"Error merging dictionaries for key [bold]{override_key}[/bold] : {exception}",
                    )
                    raise

                yaml_dump_of_merged = yaml.dump(data=merged, sort_keys=False)
                log_action(
                    action="After merging dictionaries",
                    action_style="yellow",
                    object_name='',  # if 'name' in merged else ''  ?
                    details=yaml_dump_of_merged,
                )

            elif isinstance(override_value, list) and isinstance(base_value, list):
                # logger.debug("", alt=f"[blue]Before list :[/blue]\n{yaml.dump(merged)}")
                yaml_dump_of_merged = yaml.dump(data=merged, sort_keys=False)
                log_action(
                    action="Before merging lists",
                    action_style="dim blue",
                    object_name=f"{base_value_name} into {override_value_name}",
                    details=yaml_dump_of_merged,
                )
                base_list = base_value
                try:
                    merged[override_key] = merge_lists(
                        base_list=base_list,
                        override_list=override_value,
                    )
                except Exception as e:
                    logger.error(f"Error merging lists for key {override_key} : {e}")
                    raise

                yaml_dump_of_merged = yaml.dump(data=merged, sort_keys=False)
                log_action(
                    action="After merging lists",
                    action_style="bold blue",
                    object_name='',  # if 'name' in merged else ''  ?
                    details=yaml_dump_of_merged,
                )

            else:
                log_action(
                        action="No dictionaries or lists, hence overwriting", # alt=f"[red]No dictionaries or lists[/red], hence [underline]overwriting[/underline] :
                        action_style='bold red',
                        object_name=override_key,
                        details=f"{override_key} = {override_value}",  # [code]{override_key}[/code] = [bold]{override_value}[/bold]\n",
                        )
                merged[override_key] = override_value
                yaml_dump_of_merged = yaml.dump(data=merged, sort_keys=False)
                log_action(
                    action="After direct assignment",
                    action_style="bold red",
                    object_name=f"{override_key} = see: `override_value`",
                    details=yaml_dump_of_merged,
                )

        else:
            log_node(
                node_type='Child',  # the child key actually
                key=override_key,
                state_message="does not exist in Parent !",
                message_style='red'
            )
            log_action(
                    action=f"Adding",
                    action_style='green',
                    object_name=override_key,
                    details=f'{override_key} = {override_value}',
                    )
            merged[override_key] = deepcopy(override_value)
            # merged[override_key] = override_value
            yaml_dump_of_merged = yaml.dump(merged, sort_keys=False)
            log_action(
                action="After adding",
                action_style="magenta",
                object_name=f"{override_key}",
                details=yaml_dump_of_merged,
            )

    # Special handling for nested sections
    if 'sections' in merged and 'sections' in override:
        for section_key, section_value in override['sections'].items():
            if section_key in merged['sections']:
                merged['sections'][section_key] = merge_dictionaries(
                    base=merged['sections'][section_key],
                    override=section_value,
                )
            else:
                merged['sections'][section_key] = deepcopy(section_value)

    yaml_dump_of_merged = yaml.dump(data=merged, sort_keys=False)

    if 'name' in merged and not isinstance(merged['name'], dict):
        action = "consolidated"
        action_style = 'bold green'
        merged_data_model_name = merged['name']
    else:
        action = "partially consolidated"
        action_style = ''
        merged_data_model_name = ''

    log_action(
            action=f"Return {action}",
            action_style=action_style,
            object_name=merged_data_model_name,
            details=yaml_dump_of_merged,
            )

    return merged


# def deep_merge(base: dict, override: dict) -> dict:
#     """
#     Recursively merges two dictionaries. Values in `override` will overwrite
#     those in `base` if keys match. If both values are dictionaries, they are
#     merged recursively. For lists, items are appended if they don't already exist.
#     """
#     merged = base.copy()
#     for key, value in override.items():
#         if key in merged:
#             if isinstance(merged[key], dict) and isinstance(value, dict):
#                 merged[key] = deep_merge(merged[key], value)
#             elif isinstance(merged[key], list) and isinstance(value, list):
#                 for item in value:
#                     if item not in merged[key]:
#                         merged[key].append(item)
#             else:
#                 merged[key] = value
#         else:
#             merged[key] = value
#     return merged


def deep_merge(base, override):
    """
    Recursively merge two dictionaries or lists without overwriting.
    - Dicts: merged recursively.
    - Lists of dicts: merged by first common key (section, subsection, id, name), else append unique.
    - Lists of other types: append unique items.
    """
    if isinstance(base, dict) and isinstance(override, dict):
        merged = base.copy()
        for key, value in override.items():
            if key in merged:
                merged[key] = deep_merge(merged[key], value)
            else:
                merged[key] = value

        return merged


    elif isinstance(base, list) and isinstance(override, list):
        #
        # return base + [item for item in override if item not in base]
        #
        # Merge lists of dicts by identifier key
        if all(isinstance(item, dict) for item in base + override):
            id_keys = ['subsection', 'section', 'id', 'name']
            identifier = next((k for k in id_keys if k in (base[0] if base else {})), None)
            if identifier:
                base_map = {item[identifier]: item for item in base if identifier in item}
                override_map = {item[identifier]: item for item in override if identifier in item}
                merged = []
                seen_ids = set()
                for item in base:
                    item_id = item.get(identifier)
                    if item_id in override_map:
                        merged.append(deep_merge(item, override_map[item_id]))
                        seen_ids.add(item_id)
                    else:
                        merged.append(item.copy())
                for item in override:
                    item_id = item.get(identifier)
                    if item_id not in seen_ids:
                        merged.append(item.copy())
                return merged
        # Fallback: append unique items
        merged = base.copy()
        for item in override:
            if item not in merged:
                merged.append(item)
        return merged
    else:
        return override

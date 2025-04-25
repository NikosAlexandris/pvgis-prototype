import copy
from typing import Dict, Any, List


def merge_lists(base_list: List[Any], override_list: List[Any]) -> List[Any]:
    """Merge two lists by recursively merging dictionaries found within them."""
    merged_list = []
    base_sections = {item.get("section") for item in base_list if isinstance(item, dict)}

    for override_item in override_list:
        if isinstance(override_item, dict):
            if override_item.get("section") in base_sections:
                base_item = next(
                    item
                    for item in base_list
                    if item.get("section") == override_item.get("section")
                )
                merged_list.append(merge_dictionaries(base_item, override_item))
            else:
                merged_list.append(override_item)
        else:
            merged_list.append(override_item)

    for base_item in base_list:
        if isinstance(base_item, dict) and base_item.get("section") not in {
            item.get("section") for item in merged_list
        }:
            merged_list.append(base_item)

    return merged_list


def merge_dictionaries(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries recursively."""
    merged = copy.deepcopy(base)  # Use deep copy

    for key, value in override.items():
        if key in merged:
            if isinstance(value, dict) and isinstance(merged[key], dict):
                merged[key] = merge_dictionaries(merged[key], value)
            elif isinstance(value, list) and isinstance(merged[key], list):
                merged[key] = merge_lists(merged[key], value)
            else:
                merged[key] = value
        else:
            merged[key] = value
    return merged

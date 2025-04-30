import copy
from typing import Dict, Any, List
# from rich import print


def merge_lists(
    base_list: List[Any] | None, override_list: List[Any] | None
) -> List[Any] | None:
    """
    Merge two lists by recursively merging dictionaries found within them. For
    example, given a `base` and an `override` list :

        base = [ {'a': 1}, {'b': 2}]
        override = [ {'c': 1}, {'a': 2}]

    the `override` list is merged into the `base` which is then the final
    output :

        base = [ {'a': 2}, {'b': 2}, {'c': 1} ]

    """
    if override_list is None:
        return base_list

    if base_list is None:
        return override_list

    merged_list = []
    # Track sections in `base`
    base_sections = {item.get("section") or item.get("subsection") for item in base_list if isinstance(item, dict)}

    for override_item in override_list:
        if isinstance(override_item, dict):
            # If the override `section` exists in the base list, merge it
            key = override_item.get("section") or override_item.get("subsection")
            if key in base_sections:
                # Find the corresponding base `section`
                base_item = next(
                    item
                    for item in base_list
                    if item.get("section") == key or item.get("subsection") == key
                )
                # Merge the `override` section into the `base` one
                merged_list.append(merge_dictionaries(base_item, override_item))
            else:
                # If `section` doesn't exist in base, add it directly
                merged_list.append(override_item)
        else:
            # If it's not a dictionary, add it directly too !
            merged_list.append(override_item)

    # Add base item/s not overriden
    for base_item in base_list:
        if isinstance(base_item, dict):
            base_key = base_item.get("section") or base_item.get("subsection")
            if base_key  not in {
                    item.get("section")
                    or item.get("subsection")
                    for item in merged_list
                    if isinstance(item, dict)
            }:
                merged_list.append(base_item)
            else:
                if base_item not in merged_list:
                    merged_list.append(base_item)

    return merged_list


def merge_lists_x(
    base_list: List[Any] | None, override_list: List[Any] | None
) -> List[Any] | None:
    """
    """
    if override_list is None:
        return base_list

    if base_list is None:
        return override_list

    # Group all items (from both lists) by their 'section' key
    all_items = base_list + override_list
    grouped: Dict[str | None, List[Dict]] = {}

    for item in all_items:
        if isinstance(item, dict):
            section = item.get("section") or item.get("subsection")
            grouped.setdefault(section, []).append(item)
        else:
            grouped.setdefault(None, []).append(item)

    merged_list = []
    for section, items in grouped.items():
        if section is None:
            # Non-dict items are added directly
            merged_list.extend(items)
            continue

        # Merge all dicts with this 'section' key
        merged_section = items[0].copy()
        for item in items[1:]:
            merged_section = merge_dictionaries(merged_section, item)
        merged_list.append(merged_section)

    return merged_list


# def merge_lists(
#     base_list: List[Any] | None, override_list: List[Any] | None
# ) -> List[Any] | None:
#     """
#     Merge two lists by recursively merging dictionaries found within them. For
#     example, given a `base` and an `override` list :

#         base = [ {'a': 1}, {'b': 2}]
#         override = [ {'c': 1}, {'a': 2}]

#     the `override` list is merged into the `base` which is then the final
#     output :

#         base = [ {'a': 2}, {'b': 2}, {'c': 1} ]

#     """
#     print(f"[dim bold]Merging lists[/dim bold]")
#     if override_list is None:
#         return base_list

#     if base_list is None:
#         return override_list

#     merged_list = []

#     # Track sections in `base`
#     base_sections = {item.get("section") for item in base_list if isinstance(item, dict)}

#     for override_item in override_list:
#         print(f"[bold]Override[/bold] object : [code]{override_item=}[/code]")
#         if isinstance(override_item, dict):

#             # If the override `section` exists in the base list, merge it
#             if override_item.get("section") in base_sections:

#                 # Find the corresponding base `section`
#                 base_item = next(
#                     item
#                     for item in base_list
#                     if item.get("section") == override_item.get("section")
#                 )
#                 print(f"[bold]Base[/bold] object : {base_item=}")
#                 # Merge the `override` section into the `base` one
#                 print(f"Before : {merged_list=}")
#                 merged_list.append(merge_dictionaries(base_item, override_item))
#                 print(f"After : {merged_list=}")
#                 print()

#             else:
#                 # If `section` doesn't exist in base, add it directly
#                 merged_list.append(override_item)
#                 print(f"After : {merged_list=}")
#                 print()

#         else:
#             # If it's not a dictionary, add it directly too !
#             print(f"[dim]Override object is not a dictionary, adding directly[/dim]")
#             merged_list.append(override_item)
#             print()


#     for base_item in base_list:
#         if isinstance(base_item, dict) and base_item.get("section") not in {
#             item.get("section") for item in merged_list
#         }:
#             merged_list.append(base_item)

#     return merged_list


def merge_dictionaries(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries recursively."""
    if override is None:
        # print(f"Override is None, returning {base=}")
        # print()
        return base

    else:
        merged = copy.deepcopy(base)  # Safe copy !
        # print(f"Keys in base : {merged.keys()=} ")
        # print(f"Keys in Override : {override.keys()=}")
        for key, value in override.items():
            # print(f"Override {key=} : {value=}")
            # print(f"{type(value)=} : {type(key)=}")
            

            if key in merged:
                # print(f"Override {key=} exists in base")
                # print(f"Override {value=}")
                # print(f"Base value for {key=} is {merged[key]=}")
                

                if isinstance(value, dict) and isinstance(merged[key], dict):
                    # print(f"[dim]Merging dictionaries[/dim]")
                    merged[key] = merge_dictionaries(merged[key], value)
                # elif isinstance(value, list):
                #     print(f"Override {key=} contains a list : {value=}")
                #     print(f"Corresponding base value is : {merged[key]=} ")
                #     print()


                elif isinstance(value, list) or value is None:# and isinstance(merged[key], list):
                    # print(f"Override {key=} contains a list : {value=}")
                    # print(f"Corresponding base is : {merged=} ")
                    # print()
                    merged[key] = merge_lists_x(merged[key], value)
                

                else:
                    if merged[key] != value:
                        # print(f"Before : Merge {value=} with {key=} to {merged=}")
                        merged[key] = value
                        # print(f"After : {merged=}")
                        # print()
            else:
                merged[key] = value

        return merged

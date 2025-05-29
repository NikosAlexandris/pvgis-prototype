from copy import deepcopy
from pvgisprototype.core.factory.definition.merge import deep_merge
from pvgisprototype.core.factory.log import logger


# Template metadata keys that should be excluded from final structure items
TEMPLATE_METADATA_KEYS = {'sections', 'require', '_file_path'}


def merge_structure_list(
    base_structure,
    override_structure,
):
    """
    Merge output structures, including nested lists/dicts.
    """
    if not override_structure:
        # Case 2: Child is placeholder - inherit full parent structure
        logger.debug(
            f"No output structure in the child node -- inheriting parent node entirely!\n\n{base_structure=}\n"
        )
        return deepcopy(base_structure)

    # Case 1: Merge structures and assign back
    logger.debug(
        "/ Merging child output structure into the parent output structure",
        alt=f"/ Merging child output structure into the parent output structure",
    )

    # Create a map of parent sections for quick lookup
    parent_sections = {
        # item["section"]: item for item in base_structure if "section" in item
        item.get('section'): item for item in base_structure
    }
    logger.debug(
        f"A map of `sections` in the parent node\n\n{parent_sections=}\n",
        # alt=f"A map of `sections` in the parent node\n\n{parent_sections}",
    )
    merged = []

    # First process all child items
    for child_item in override_structure:
        section_name = child_item.get("section")

        if section_name in parent_sections:

            # Retrieve parent item
            parent_item = parent_sections.pop(section_name)
            logger.debug(
                f"Matching child section\n\n{section_name=}\n\n   {child_item=}\n\nin parent node is\n\n   {parent_item=}\n"
            )

            # Remove require directive if present
            if "require" in child_item:
                logger.debug(f"Poping the require directive")
                child_item.pop("require", None)

            # Create merged item with parent as base
            logger.debug(f"Inheriting from parent node")
            merged_item = deep_merge(parent_item, child_item)  # deepcopy

            # Remove template metadata from the final structure item
            for key in TEMPLATE_METADATA_KEYS:
                merged_item.pop(key, None)

            logger.debug(f"Updated child node\n\n{merged_item=}\n")
            merged.append(merged_item)
            # logger.debug(f"Updated output structure\n\n{merged=}\n")

        else:
            logger.debug(
                f"No matching child section `{section_name=}` in parent node."
                + f"Preserve existing child item\n\n   {child_item=}\n"
            )
            # merged.append(deepcopy(child_item))
            # Clean child item before adding
            clean_child = {k: v for k, v in child_item.items() 
                          if k not in TEMPLATE_METADATA_KEYS}
            merged.append(clean_child)

    # Add remaining parent items not overridden by child
    # merged.extend(parent_sections.values())
    # merged.extend(deepcopy(item) for item in parent_sections.values())

    # Add remaining parent items (also cleaned)
    for parent_item in parent_sections.values():
        clean_parent = {k: v for k, v in parent_item.items() 
                       if k not in TEMPLATE_METADATA_KEYS}
        merged.append(clean_parent)

    logger.debug(f"Updated output structure\n\n{merged=}\n")

    return merged

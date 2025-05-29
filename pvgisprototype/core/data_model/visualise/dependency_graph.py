from collections import defaultdict
from pathlib import Path
import yaml
from pvgisprototype.core.factory.log import logger


def build_dependency_graph(
    source_path: Path,
) -> dict:
    """
    Build a directed graph of data model dependencies
    """
    graph = defaultdict(list)
    base_dir = Path(source_path.parts[0]) #if source_path.is_dir() else source_path.parent
    path_to_name = {}

    logger.info(f"Input path : {source_path=}")
    
    # Check if the source_path is a file or a directory
    if source_path.is_file() and source_path.suffix == '.yaml':
        # Process a single YAML file
        logger.info(f"Processing single file: {source_path}")
        with open(source_path, 'r') as f:
            data = yaml.safe_load(f)
            model_name = data.get('name')
            path_to_name[source_path.name] = model_name  # Map the file name to its model name
            if 'require' in data:
                requires = data['require']
                if not isinstance(requires, list):
                    requires = [requires]
                for req in requires:
                    # Append the requirement as is for now
                    with open( Path(base_dir / req).with_suffix('.yaml'), 'r') as parent_file:
                        parent_data = yaml.safe_load(parent_file)
                        parent_data_name = parent_data['name']
                        graph[model_name].append((parent_data_name, req))  # Append the requirement path

    elif source_path.is_dir():
        # Process all YAML files in the directory
        for yaml_file in source_path.glob("*.yaml"):
            logger.info(f"Processing {yaml_file}")
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                model_name = data.get('name')
                path_to_name[yaml_file.name] = model_name  # Map the file name to its model name
                if 'require' in data:
                    requires = data['require']
                    if not isinstance(requires, list):
                        requires = [requires]
                    for req in requires:
                        # Append the requirement path
                        graph[model_name].append(req)  # Append the requirement path
    else:
        logger.error(f"Invalid path: {source_path}. It must be a YAML file or a directory containing YAML files.")
        raise ValueError("Invalid path. Please provide a valid YAML file or directory.")

    # Now we need to replace the paths in the graph with the corresponding names
    for parent, children in graph.items():
        for i, child in enumerate(children):
            # If the child is a path, replace it with the corresponding name
            if child in path_to_name:
                children[i] = path_to_name[child]  # Replace with the name

    return dict(graph)

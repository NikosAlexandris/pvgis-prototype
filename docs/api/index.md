---
icon: material/language-python
tags:
  - API
  - Core API
  - Python API
  - How-To
---

This section demonstrates how to use the API programmatically.

!!! note "Install me first!"

    [Installation instructions](../install/index.md)

## API tree

To start with,
we can overview the contents of the `api` directory

```python exec="true" result="tree"
from pathlib import Path

def print_tree(directory, level=1):
    directory = Path(directory)
    if not directory.is_dir():
        return  # ensure it's a directory

    # list first level files and directories
    tree = str()
    for path in sorted(directory.iterdir()):
        if path.name.startswith('_'):
            continue  # skip files or directories starting with '_'
        if path.is_dir():
            tree += f"    {path.name}/"  # add slash to indicate it's a directory
        else:
            tree += f"    {path.name}"
        tree += '\n'

    return tree

tree = print_tree('pvgisprototype/api/')
print(tree)
```

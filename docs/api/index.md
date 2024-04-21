---
icon: material/language-python
tags:
  - API
  - Core API
  - Python API
  - How-To
---

This section contains How-To recipes and simple examples in using the API programmatically.

!!! seealso "Install me first!"

    [Installation instructions](../install/index.md)


## API tree

To start with,
we can overview the contents of the `api` directory

```python exec="true"
from pathlib import Path


def print_tree(directory, level=1):
    directory = Path(directory)
    if not directory.is_dir():
        return  # Ensure it's a directory

    # Only list the first level of files and directories
    tree = str()
    for path in sorted(directory.iterdir()):
        if path.name.startswith('_'):
            continue  # Skip files or directories starting with '_'
        if path.is_dir():
            tree += f"\n    {path.name}/"  # Add slash to indicate it's a directory
        else:
            tree += f"\n    {path.name}"

    # Optionally print a trailing line after listing
    if level == 1:
        tree += '\n   '

    return tree

tree = print_tree('pvgisprototype/api/')
print(f"```\n{tree}\n```")
```

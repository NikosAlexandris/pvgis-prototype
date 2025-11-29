---
icon: material/new-box
title: New Feature?
tags:
  - Development
  - Contribution
  - New Features
  - Source Code
  - Reference
  - Algorithms
  - API
  - CLI
  - Web API
---

!!! danger "Update-Me"

    Add guidelines on adding a new feature.

# Adding New Features in PVGIS' API

:material-check-decagram: If you know your ways around Python,
it should be not difficult to add a :material-new-box: new feature
(i.e. an algorithm or some helper function)
in PVGIS' API!

Given a working implementation of a function of interest in Python,
preferrably using NumPy,
the steps to integrate it in PVGIS' API are:

1. add the function as a Python module under the `algorithms` directory
2. add a new function under the `api` directory
3. optionally, add a new Typer-based command for the command line interface
4. optionally, add a new FastAPI-based entrypoint

## Developing a new function

[Guide on how to develop custom extensions, including necessary tools and practices]

## Integration with PVGIS' API

[Instructions on how to integrate custom extensions with the API]

## Sharing Your Function

[Provide information on how users can share their custom functions]

For more advanced features, see our [Advanced Usage](../tutorials/advanced_usage.md) section.

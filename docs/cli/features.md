---
icon: material/view-grid-plus
title: Features
description: Welcome in PVGIS' CLI
tags:
  - How-To
  - CLI
  - Features
  - Help
  - Auto-Completion
  - Logging
  - Debugging
---

## Overview

<div class="grid cards" markdown>

- :material-help: __Help__

    ---

    For each command,
    there is a `--help` option.

- :octicons-versions-24: __Versioning__

    ---

    Which version of the software am I running ?

    ``` bash
    pvgis-prototype --version
    ```

- :octicons-command-palette-24: __Auto-Completion__

    ---

    Auto-completion in the command line ?

    ``` bash
    pvgis-prototype completion --help
    ```

</div>

## Help

For each and every command,
there is a `--help` option.
Please consult it to grasp the details for
a command,
its arguments and optional parameters,
default values
and settings that can further shape the output.

For example,

``` bash exec="0"
pvgis-prototype
```

or

``` bash exec="0"
pvgis-prototype --help
```

??? question "Example"

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype --help
    ```

## Version :octicons-versions-24:

It might be useful to know which version of the software we have installed :


``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype --version
```

## Auto-Completion

Auto-completion in the command line can be installed optionally.
This is offered via the _hidden_ command `completion`.

!!! tip "Auto-completion in the command line :material-cursor-text:"

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype completion --help
    ```

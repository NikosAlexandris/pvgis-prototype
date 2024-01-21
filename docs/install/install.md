---
hide:
  - navigation
tags:
  - Python
  - install
  - pip
  - virtual environment
---

# Install

!!! danger "Under Development"

    **Everything is under development and subject to change!**

## Requirements

- An operating system that supports Python
- A Python virtual environment

## Install

To begin with,
**create a [virtual environment][venv]!**

[venv]: https://docs.python.org/3/library/venv.html

Next,
you can install PVIS in the following way :

1. Clone the source code repository
2. Step in the source code directory
3. Install the Python package

<div class="termy">

```console
$ git clone https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype
$ cd pvis-be-prototype
$ pip install ."[all]"
---> 100%
Successfully installed pvis
```

</div>

!!! warning

    PVIS is under development so for the time being you may want to install
    either _all_ dependencies or the _dev_ ones.  For the latter option,
    you can do
    ``` bash
    pip install .[dev]`.
    ```

!!! note

    The installation will include
    <a href="https://rich.readthedocs.io/" class="external-link" target="_blank">Rich</a>.
    Rich is a library to *display* visually pleasing information on the terminal.
    It is deeply integrated into **PVIS**.

## Welcome !

Then,
welcome yourself in the command line interface by executing 

``` bash exec="true" result="ansi" source="above"
pvgis-prototype --help
```

## Auto-completion

!!! tip "Auto-completion in the command line"

    Auto-completion in the command line can be installed optionally.
    This is offered via the _hidden_ command `completion` :

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype completion show --help
    ```

## Help ?

Check the dedicated [help](help.md) page.

---
icon: material/tools
tags:
  - Python
  - install
  - pip
  - virtual environment
---

|Git clone|pvis-be-prototype|link:https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype|copy:git clone https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype.git|
|Install via pip|pip install git+|link:https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype|copy:pip install git+https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype.git|

# Install

!!! danger "Under Development"

    **Everything is under development and subject to change!**

## Requirements

- An operating system that supports Python
- A Python virtual environment

## Environment setup

To begin with,
**create a [virtual environment][venv]!**

[venv]: https://docs.python.org/3/library/venv.html

## Install

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
    
    This will install _all_ of : the core API, the CLI and the Web API.

!!! note

    The installation will include
    <a href="https://rich.readthedocs.io/" class="external-link" target="_blank">Rich</a>.
    Rich is a library to *display* visually pleasing information on the terminal.
    It is deeply integrated into **PVIS**.

## CLI

Hello and welcome yourself in the PVGIS command line interface (CLI) : 

``` bash exec="true" result="ansi" source="above"
pvgis-prototype
```

!!! hint

    All commands run _without_ arguments,
    will display the help overview,
    just as if we run them with `--help`.

!!! tip "Auto-completion in the command line"

    Auto-completion in the command line can be installed optionally.
    This is offered via the _hidden_ command `completion` :

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype completion show --help
    ```

## Web API

If you wish to test/run the Web API, you can run it locally as follows :

<div class="termy">

``` console
$ cd pvgisprototype
$ uvicorn pvgisprototype.webapi:app --reload
INFO:     Will watch for changes in these directories: ['pvgis-prototype']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [134186] using StatReload
INFO:     Started server process [134188]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

By default, the server will run on http://127.0.0.1:8000.
We can run on another address, like so :

<div class="termy">

``` console
$ cd pvgisprototype
$ uvicorn pvgisprototype.webapi:app --reload --host 127.0.0.2
INFO:     Will watch for changes in these directories: ['pvgis-prototype']
INFO:     Uvicorn running on http://127.0.0.2:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [134186] using StatReload
INFO:     Started server process [134188]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>


Click on the URL and you should be landing in a page like

<!-- <figure markdown> -->
  ![PVGIS Web API](../images/pvgis-prototype_web_api_uvicorn_2024-01-26.png)
  <!-- <figcaption>Image caption</figcaption> -->
<!-- </figure> -->

## Help ?

Check the dedicated [help](help.md) page.

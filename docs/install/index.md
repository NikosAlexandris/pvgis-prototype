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
**create a Python [virtual environment][venv]!**
and activate it:

``` bash
python -m venv pvgis-virtual-environment
source pvgis-virtual-environment/bin/activate
```

[venv]: https://docs.python.org/3/library/venv.html

!!! tip

    Forgetting to activate a virtual environment will install various packages 
    outside virtual environments at a system-wide level
    which, over time, will likely lead to errors.

    By setting for example in `.bashrc` or `.zshrc`
    the environment variable `PIP_REQUIRE_VIRTUALENV` to `true`
    and re-starting your shell,
    `pip` will refuse to install anything outside a virtual environment.

    ``` bash
    export PIP_REQUIRE_VIRTUALENV=true
    ```

???+ tip

    Regardless of our favourite programming language
    or tool to manage environments,
    chances are high we'd benefit from using [`direnv`][direnv].
    In the context of a Python package, like [`rekx`][rekx],
    `direnv` supports all such well known tools
    from standard `venv`, `pyenv` and `pipenv`,
    to `anaconda`, `Poetry`, `Hatch`, `Rye`
    and `PDM`.
    Have a look at [direnv's Wiki page for Python][direnv-wiki-python].

    `rekx` is developed inside a virtual environment
    (re-)created and (re-)activated via `direnv`.
    The following `.envrc` does all of it :
    
    ``` title=".envrc"
    --8<-- ".envrc"
    ```

    Find more about `layout python` in
    [direnv/wiki/Python#venv-stdlib-module](https://github.com/direnv/direnv/wiki/Python#venv-stdlib-module).

## Install

Next,
and once inside a dedicated virtual environment,
we can install PVIS in the following way :

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

## For Developers and Power Users

Curious to explore the latest (non-released development) version ?
Want to modify some function or add a new one and contribute to PVGIS ?

Using [PDM][PDM],
you can seamlessly establish a virtual environment
and install PVGIS in an editable mode.

[PDM]: https://pdm-project.org/latest/

The inclusion of a `pdm.lock` file in the source code repository,
ensures the installation of the exact dependencies needed
to setup a development environment.

1. Clone the latest version from the source repository :

``` bash
git clone https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype.git
cd pvis-be-prototype
```

2. Install PVGIS using PDM

``` bash
pdm install
```
This will create a virtual environment
and install PVGIS along with its dependencies.

3. Activate the virtual environment

``` bash
$ eval $(pdm venv activate in-project)
```

* Alternatively, it is possible to run 

[Run a command in a virtual environment without activating it](https://pdm-project.org/latest/usage/venv/#run-a-command-in-a-virtual-environment-without-activating-it)

Happy coding!


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

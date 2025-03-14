---
icon: material/tools
tags:
  - Install
  - Python
  - Git
  - Python virtual environment
  - venv
  - direnv
  - pip
  - PDM
  - Dependencies
---

|Git clone|pvis-be-prototype|link:https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype|copy:git clone https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype.git|
|Install via pip|pip install git+|link:https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype|copy:pip install git+https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype.git|

!!! danger "Under Development"

    **Everything is under development and subject to change!**

# Requirements

- An [operating system that supports Python][python-operating-systems]
- A [Python virtual environment][python-virtual-environment]

[python-operating-systems]: https://www.python.org/downloads/operating-systems/
[python-virtual-environment]: https://peps.python.org/pep-0405/


# Environment setup

To begin with,
**create a Python [virtual environment][venv]!**
and activate it :

``` bash
python -m venv pvgis-virtual-environment
source pvgis-virtual-environment/bin/activate
```

[venv]: https://docs.python.org/3/library/venv.html

??? tip "Disallow to install outside a virtual environment"

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

??? tip "Use `direnv` to work seamlessly with virtual environments"

    Regardless of our favourite programming language
    or tool to manage environments,
    chances are high we'd benefit from using [`direnv`][direnv].
    In the context of a Python package,
    `direnv` supports all such well known tools
    from standard `venv`, `pyenv` and `pipenv`,
    to `anaconda`, `Poetry`, `Hatch`, `Rye`
    and `PDM`.
    Have a look at [direnv's Wiki page for Python][direnv-wiki-python].

    `pvgisprototype` is developed inside a virtual environment
    (re-)created and (re-)activated via `direnv`.
    The following `.envrc` does all of it :
    
    ``` title=".envrc"
    --8<-- ".envrc"
    ```

    Find more about `layout python` in [direnv/wiki/Python#venv-stdlib-module][direnv-wiki-python-venv].

    [direnv-wiki-python]: https://github.com/direnv/direnv/wiki/Python

    [direnv-wiki-python-venv]: https://github.com/direnv/direnv/wiki/Python#venv-stdlib-module


# Simple install

Once inside a dedicated virtual environment,
we can install PVIS with a single command
using [pip][pip],
Python's standard package installer :

[pip]: https://pip.pypa.io

<div class="termy">

```console
$ pip install git+https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype.git@v0.8.3
---> 100%
..
Building wheels for collected packages: pvgisprototype
  Building wheel for pvgisprototype (pyproject.toml) ... done
  Created wheel for pvgisprototype: filename=pvgisprototype-0.8.3-py3-none-any.whl size=32225753 sha256=3c658cf43ab6e7913bbacabd51344948e420b7b875a0fa7e174b00f9fc98a50e
  Stored in directory: /tmp/pip-ephem-wheel-cache-ra_n3wre/wheels/a6/36/0f/97514dbae676105e1d4f6f9581498547b769a5fbd3afe74ca9
Successfully built pvgisprototype
..
```

</div>

!!! info

    The above is a one-step installation of a specific tagged/release version
    of the software from its source code Git repository.


# For Developers

Are you a developer or a Power-User ?
Curious to explore the latest (non-released development) version ?
Want to modify some function or add a new one and contribute to PVGIS ?
You can install PVIS in an [editable mode][editable-installs].

## pip install -e

[editable-installs]: https://pip.pypa.io/en/latest/topics/local-project-installs/#editable-installs

1. Clone the source code repository

    <div class="termy">
    ```console
    $ git clone https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype
    ```
    </div>

2. Step in the source code directory

    <div class="termy">
    ```console
    $ cd pvis-be-prototype
    ```
    </div>

3. Install in editable mode

    <div class="termy">
    ```console
    $ pip install -e ."[all]"
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


## PDM

Using [PDM][PDM],
you can seamlessly establish a virtual environment
and install PVGIS in an _editable mode_.

[PDM]: https://pdm-project.org/latest/

The inclusion of a `pdm.lock` file in the source code repository,
ensures the installation of the exact dependencies needed
to setup a development environment.

1. Clone the latest version from the source repository :

    <div class="termy">
    ```console
    $ git clone https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype.git
    $ cd pvis-be-prototype
    ```
    </div>

2. Install PVGIS using PDM

    <div class="termy">
    ```console
    $ pdm install
    ```
    </div>

    This will create a virtual environment
    and install PVGIS along with its dependencies.

3. Activate the virtual environment

    <div class="termy">
    ```console
    $ eval $(pdm venv activate in-project)
    ```
    </div>

* Alternatively, PDM can 
[run a command in a virtual environment without activating it](https://pdm-project.org/latest/usage/venv/#run-a-command-in-a-virtual-environment-without-activating-it)

## Conda

In order to install the software using [conda](https://anaconda.org/anaconda/conda) (instructions for installing conda can be found [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html#)):

1. First clone the software to get the latest changes:

    <div class="termy">

    ```console
    $ git clone https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype
    ---> 100%
    ```

    </div>

2. Then, navigate into the source code directory:

    <div class="termy">

    ```console
    $ cd pvis-be-prototype
    ```

    </div>

3. Create the conda environment by running the following command. This will create an new conda environment named `pvgis` and install the PVGIS software along with its dependencies using the `environment.yml` file that is distributed with the software:

    <div class="termy">

    ```console
    $ conda env create
    ---> 100%
    ```

    </div>

4. Finally, activate the conda environment:

    <div class="termy">

    ```console
    $ conda activate pvgis
    ```

    </div>


# Verify

We can verify the installation was successful
by running any command (i.e. `pvgis-prototype`)
or asking for the version of the installed package :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype --version
```

**That was it!** **Happy coding!**

# After the installation ..

- Interact with PVIS through the [command line interface (CLI)](cli/index.md)
- Run the [Web API](web_api/index.md) server
- Use the [API](api/index.md) in your scripts

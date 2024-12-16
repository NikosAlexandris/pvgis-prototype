[![pipeline status](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/badges/mkdocs/pipeline.svg)](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/commits/mkdocs) 
[![coverage report](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/badges/mkdocs/coverage.svg)](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/commits/mkdocs) 
[![Latest Release](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/badges/release.svg)](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/releases) 


**Attention** details and links might be outdated.  Please check the
documetation for updated Information : 

https://nikosalexandris.gitlab.io/photovoltaic-information-system/

You may want to build the documetation yourself,
in which case see instruction below.

# Photovoltaic (Geographic) Information System

[PVGIS][PVGIS]
is an open [web application][PVGIS Web Application]
of the :flag_eu: European Commission.
It is developed and maintained
in the [Joint Research Centre (JRC)][JRC]
for over two decades
by the Energy Efficiency and Renewables Unit (Ispra) of the Energy,
Transport and Climate directorate.

[JRC]: https://joint-research-centre.ec.europa.eu/index_en

## Features & Capabilities

PVGIS
offers cost-free public service insights
on solar radiation and photovoltaic performance,
providing location-specific estimates of power output
for systems using various PV technologies.


- __Photovoltaic Potential__ for various technologies for Grid-connected & Stand-alone systems

  ![Analysis of Photovoltaic Performance](docs/images/pvgis6_example_of_performance_analysis.png)

- __Solar Irradiance Analysis__ for global, direct and diffuse Irradiance based on Hofierka (2004)

  ![Analysis of Solar Irradiance Components](docs/images/pvgis6_example_of_solar_irradiance_analysis.png)

- __Solar Position Analysis__ based on various algorithms, the defaul being NOAA's solar geometry model

  ![Analysis of Solar Position](docs/images/pvgis6_example_of_solar_positioning.png)

- [Fingerprint](cli/fingerprint.md)ed reproducible calculations & [QR-Code](cli/qrcode.md) shareable results
  
  <img src="docs/images/pvgis6_example_of_performance_analysis_qr_code.png" alt="QR-Code" width="200"/>

- __Time Series__ of

    - Photovoltaic Performance 
    - Solar Radiation
    - Temperature & Wind Speed 
    - Typical Meteorological Year for 9 climate variables and multiple methods
      <img src="./typical_meteorological_year.png" alt="QR-Code" width="600"/>
    
- __Coverage & Maps__ [^1]

    [^1]: Printing ? [:thinking: https://thinkbeforeprinting.org/](https://thinkbeforeprinting.org/)

    - Europe & Africa :earth_africa:
    - Largely Asia :earth_asia:
    - America :earth_americas:
    - Country/regional maps of solar resource & PV potential

- __Public Service__

    - Supported by the 🇪🇺 European Commission
    - Cost free
    - Open access
    - [> 50K Web API requests / week](reference/web_traffic.md)

- __Open by design__

    ![](images/Logo_EUPL.svg.png){align=right height=100px width=100px}

    - Python [API](#) based on :simple-numpy: NumPy
    - [Web API](#) based on :simple-fastapi: FastAPI
    - [CLI](#) based on Typer
    - Open Source [License](#) EUPL-1.2

-  __Languages__

    ![](images/languages-in-pvgis.svg){align=right height=100px width=100px}

    - English
    - French  |  German
    - Spanish  |  Italian

<!-- vim-markdown-toc GitLab -->

* [Installation](#installation)
    * [Requirements](#requirements)
    * [Environment setup](#environment-setup)
    * [Simple install](#simple-install)
    * [For Developers](#for-developers)
        * [pip install -e](#pip-install-e)
        * [PDM](#pdm)
        * [Conda](#conda)
    * [Verify](#verify)
    * [After the installation ..](#after-the-installation-)
* [Contact and Support](#contact-and-support)

<!-- vim-markdown-toc -->

# Installation

See https://nikosalexandris.gitlab.io/photovoltaic-information-system/install/.

## Requirements

- An [operating system that supports Python][python-operating-systems]
- A [Python virtual environment][python-virtual-environment]

[python-operating-systems]: https://www.python.org/downloads/operating-systems/
[python-virtual-environment]: https://peps.python.org/pep-0405/


## Environment setup

To begin with,
**create a Python [virtual environment][venv]!**
and activate it :

``` bash
python -m venv pvgis-virtual-environment
source pvgis-virtual-environment/bin/activate
```

[venv]: https://docs.python.org/3/library/venv.html

> **Tip !** 
> **Disallow to install outside a virtual environment**
> 
> Forgetting to activate a virtual environment will install various packages 
  outside virtual environments at a system-wide level
  which, over time, will likely lead to errors.
>
> By setting for example in `.bashrc` or `.zshrc`
> the environment variable `PIP_REQUIRE_VIRTUALENV` to `true`
> and re-starting your shell,
> `pip` will refuse to install anything outside a virtual environment.
> 
> ``` bash
> export PIP_REQUIRE_VIRTUALENV=true
> ```

> **Tip !**
> Use `direnv` to work seamlessly with virtual environments

> Regardless of our favourite programming language
> or tool to manage environments,
> chances are high we'd benefit from using [`direnv`][direnv].
> In the context of a Python package,
> `direnv` supports all such well known tools
> from standard `venv`, `pyenv` and `pipenv`,
> to `anaconda`, `Poetry`, `Hatch`, `Rye`
> and `PDM`.
> Have a look at [direnv's Wiki page for Python][direnv-wiki-python].
> 
> `pvgisprototype` is developed inside a virtual environment
> (re-)created and (re-)activated via `direnv`.
> The following `.envrc` does all of it :
> 
> ``` title=".envrc"
> --8<-- ".envrc"
> ```
>
> Find more about `layout python` in [direnv/wiki/Python#venv-stdlib-module][direnv-wiki-python-venv].

[direnv-wiki-python]: https://github.com/direnv/direnv/wiki/Python

[direnv-wiki-python-venv]: https://github.com/direnv/direnv/wiki/Python#venv-stdlib-module


## Simple install

Once inside a dedicated virtual environment,
we can install PVIS with a single command
using [pip][pip],
Python's standard package installer :

[pip]: https://pip.pypa.io

``` bash
pip install git+https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype.git@v0.8.9
```

> The above is a one-step installation of a specific tagged/release version of
> the software from its source code Git repository.


## For Developers

Are you a developer or a Power-User ?
Curious to explore the latest (non-released development) version ?
Want to modify some function or add a new one and contribute to PVGIS ?
You can install PVIS in an [editable mode][editable-installs].

### pip install -e

[editable-installs]: https://pip.pypa.io/en/latest/topics/local-project-installs/#editable-installs

1. Clone the source code repository

    ``` bash
    $ git clone https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype
    ```

2. Step in the source code directory

    ``` bash
    $ cd pvis-be-prototype
    ```

3. Install in editable mode

    ``` bash
    $ pip install -e ."[all]"
    ```

>   PVIS is under development so for the time being you may want to install
    either _all_ dependencies or the _dev_ ones.  For the latter option,
    you can do
    ``` bash
    pip install .[dev]`.
    ```
>   
>   This will install _all_ of : the core API, the CLI and the Web API.
>
>   The installation will include
    <a href="https://rich.readthedocs.io/" class="external-link" target="_blank">Rich</a>.
    Rich is a library to *display* visually pleasing information on the terminal.
    It is deeply integrated into **PVIS**.


### PDM

Using [PDM][PDM],
you can seamlessly establish a virtual environment
and install PVGIS in an _editable mode_.

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
    eval $(pdm venv activate in-project)
    ```

* Alternatively, PDM can 
[run a command in a virtual environment without activating it](https://pdm-project.org/latest/usage/venv/#run-a-command-in-a-virtual-environment-without-activating-it)

### Conda

In order to install the software using conda (instructions for installing conda can be found [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html#)):

1. First clone the software to get the latest changes:

    ``` bash
    $ git clone https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype
    ```

2. Then, navigate into the source code directory:

    ``` bash
    $ cd pvis-be-prototype
    ```

3. Create the `conda` environment by running the following command. This will create an new `conda` environment named `pvgis` and install the PVGIS software along with its dependencies using the `environment.yml` file that is distributed with the software:

    ``` bash
    $ conda env create
    ```

4. Finally, activate the `conda` environment:

    ``` bash
    $ conda activate pvgis
    ```

## Verify

We can verify the installation was successful
by running any command (i.e. `pvgis-prototype`)
or asking for the version of the installed package :

``` bash
pvgis-prototype --version
```

**That was it!** **Happy coding!**

## After the installation ..

- Interact with PVIS through the [command line interface (CLI)](cli/index.md)
- Run the [Web API](web_api/index.md) server
- Use the [API](api/index.md) in your scripts

# Contact and Support

- Questions and comments can be sent to our mailbox:
  
  [JRC-PVGIS@ec.europa.eu](JRC-PVGIS@ec.europa.eu)

- __Postal Address__

  European Commission, Joint Research Centre
  Energy Efficiency and Renewables Unit
  via E. Fermi 2749, TP 450
  I-21027 Ispra (VA)
  Italy

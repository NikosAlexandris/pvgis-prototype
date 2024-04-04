[![pipeline status](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/badges/mkdocs/pipeline.svg)](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/commits/mkdocs) 
[![coverage report](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/badges/mkdocs/coverage.svg)](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/commits/mkdocs) 
[![Latest Release](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/badges/release.svg)](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/releases) 

# Photovoltaic Information System

[PVGIS][PVGIS]
is an open [web application][PVGIS Web Application]
of the European Commission.
Is it developed and maintained
in the [Joint Research Centre (JRC)][JRC]
for over two decades
by the Energy Efficiency and Renewables Unit (Ispra) of the Energy,
Transport and Climate directorate.

<!-- vim-markdown-toc GitLab -->

* [Installation](#installation)
    * [Requirements](#requirements)
    * [Environment setup](#environment-setup)
    * [Simple install](#simple-install)
* [Contact and Support](#contact-and-support)
* [Acknowledgments and Credits](#acknowledgments-and-credits)

<!-- vim-markdown-toc -->

# Installation

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

> **Disallow to install outside a virtual environment !**
> 
> Forgetting to activate a virtual environment will install various packages 
> outside virtual environments at a system-wide level
> which, over time, will likely lead to errors.
> 
> By setting for example in `.bashrc` or `.zshrc`
> the environment variable `PIP_REQUIRE_VIRTUALENV` to `true`
> and re-starting your shell,
> `pip` will refuse to install anything outside a virtual environment.
> 
> ``` bash
> export PIP_REQUIRE_VIRTUALENV=true
> ```

## Simple install

Once inside a dedicated virtual environment,
we can install PVIS with a single command
using [pip][pip],
Python's standard package installer :

[pip]: https://pip.pypa.io

``` bash
$ pip install git+https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype.git
```

# Contact and Support

- Questions and comments can be sent to our mailbox:
  
  [JRC-PVGIS@ec.europa.eu](JRC-PVGIS@ec.europa.eu)

- __Postal Address__

  European Commission, Joint Research Centre
  Energy Efficiency and Renewables Unit
  via E. Fermi 2749, TP 450
  I-21027 Ispra (VA)
  Italy

# Acknowledgments and Credits

- Credit to the EU Commission or any other partners or contributors.
- Acknowledgments of the original PVGIS and its impact.

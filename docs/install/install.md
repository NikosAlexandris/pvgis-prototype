---
tags:
  - Python
  - install
  - pip
  - virtual environment
---

# Installation

## Requirements

- Python

1. Clone the source code repository
2. Step in the source code directory
3. Install the Python package


## Install

<div class="termy">

```console
$ git clone https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype
$ cd pvis-be-prototype
$ pip install ."[all]"
---> 100%
Successfully installed pvis
```

</div>

!!! note

    The installation will include
    <a href="https://rich.readthedocs.io/" class="external-link" target="_blank">Rich</a>.
    Rich is a library to *display* visually pleasing information on the terminal.
    It is deeply integrated into **PVIS**.


Then, welcome yourself in the command line interface by executing 

```{.shell linenums="0"}
pvgis-prototype
```

returns (**currently**)

``` bash exec="true" result="ansi"
pvgis-prototype --help
```

For each and every command, there is a `--help` option.
Please consult it to grasp the details for a command,
its arguments and optional parameters,
default values and settings that can further shape the output.

Auto-completion in the command line can be installed optionally.
This is offered via the _hidden_ command `completion` :

```{.shell linenums="0"}
pvgis-prototype completion show --help
```
``` bash exec="true" result="ansi"
pvgis-prototype completion show --help
```

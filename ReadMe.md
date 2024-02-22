[![pipeline status](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/badges/mkdocs/pipeline.svg)](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/commits/mkdocs) 
[![coverage report](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/badges/mkdocs/coverage.svg)](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/commits/mkdocs) 
[![Latest Release](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/badges/release.svg)](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/releases) 

# Photovoltaic Information System

<!-- vim-markdown-toc GitLab -->

* [Installation](#installation)
    * [Install PVGIS](#install-pvgis)
* [Examples](#examples)
    * [CLI](#cli)
    * [API](#api)
        * [Examples](#examples-1)
    * [Contact and Support](#contact-and-support)
    * [Acknowledgments and Credits](#acknowledgments-and-credits)

<!-- vim-markdown-toc -->

# Installation

PVGIS can be installed relatively simply using `pip`.
However,
it is strongly recommended to [create a virtual environment][] first
and install PVGIS there-in.

### Install PVGIS

- Install PVGIS using pip

    - While inside the virtual environment, install `pvgis` using pip:
      ``` bash
      pip install git+https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype
      ```

- Verify Installation

    - After installation, you can verify that the package is installed
      correctly by checking its version or running a basic command, if
      available.

# Examples

- Step-by-step examples
- Cover typical and advanced use cases


## CLI

> Too long to document here !

![pvgis-prototype](pvgis-prototype-cli-2023-12-03.png)


## API 

First, run the server:

``` bash
cd pvgisprototype
uvicorn pvgisprototype.webapi:app --reload
```

Then, test some endpoints!

### Examples

```
http://localhost:8001/calculate/geometry/overview?solar_position_models=Skyfield&solar_time_model=Skyfield&apply_atmospheric_refraction=true&perigee_offset=0.048869&eccentricity_correction_factor=0.03344&angle_output_units=radians&verbose=0&longitude=8&latitude=45&timestamp=2006-12-28
```

## Contact and Support

- Information on how to get help or support.
- Contact details for reporting bugs or giving feedback.


## Acknowledgments and Credits

- Credit to the EU Commission or any other partners or contributors.
- Acknowledgments of the original PVGIS and its impact.

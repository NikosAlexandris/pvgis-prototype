# Photovoltaic Information System

<!-- vim-markdown-toc GitLab -->

* [Installation](#installation)
        * [Install PVGIS](#install-pvgis)
* [Examples](#examples)
    * [CLI](#cli)
    * [API](#api)
        * [Examples](#examples-1)
    * [Additional Resources](#additional-resources)
        * [Theoretical Background & Scientific Information](#theoretical-background-scientific-information)
            * [Wikipedia](#wikipedia)
            * [PV Education](#pv-education)
        * [Informative Articles & Dates](#informative-articles-dates)
            * [Skyfield Community Discussions](#skyfield-community-discussions)
        * [Visuals](#visuals)
    * [Frequent questions](#frequent-questions)
    * [Contact and Support](#contact-and-support)
    * [Acknowledgments and Credits](#acknowledgments-and-credits)

<!-- vim-markdown-toc -->

# Installation

PVGIS can be installed relatively simply using `pip`. However, it is rather a
good idea to [create a virtual environment][] first and install
PVGIS there-in.


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


## Additional Resources

### Theoretical Background & Scientific Information

#### Wikipedia

- [Position of the Sun](https://en.wikipedia.org/wiki/Position_of_the_Sun)
- [Equation of Time](https://en.wikipedia.org/wiki/Equation_of_time)

#### PV Education

- [Solar Time](https://www.pveducation.org/pvcdrom/properties-of-sunlight/solar-time)


### Informative Articles & Dates

#### Skyfield Community Discussions

- In Stack Exchange :

  - https://stackoverflow.com/a/69541317/1172302
  - https://astronomy.stackexchange.com/q/49580/51316

- Skyfield GitHub Discussion : https://github.com/skyfielders/python-skyfield/discussions/648

- **Multi-processing** to Improve performance of sunrise/sunset calculations in


### Visuals

- https://niwa.co.nz/our-services/online-services/solarview/solarviewexplanation


## Frequent questions

- Common issues users might encounter
- Frequently asked questions with concise answers.


## Contact and Support

- Information on how to get help or support.
- Contact details for reporting bugs or giving feedback.


## Acknowledgments and Credits

- Credit to the EU Commission or any other partners or contributors.
- Acknowledgments of the original PVGIS and its impact.

# Photovoltaic Information System

<!-- vim-markdown-toc GitLab -->

* [Introduction](#introduction)
    * [Core Functionalities](#core-functionalities)
    * [Advanced Features](#advanced-features)
    * [Data Input and Sources](#data-input-and-sources)
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
    * [Practical Applications & Tools](#practical-applications-tools)
        * [NREL (National Renewable Energy Laboratory)](#nrel-national-renewable-energy-laboratory)
        * [NOAA (National Oceanic and Atmospheric Administration)](#noaa-national-oceanic-and-atmospheric-administration)
        * [https://andrewmarsh.com/](#httpsandrewmarshcom)
            * [Applications](#applications)
            * [Significant Dates and Times](#significant-dates-and-times)
        * [Skyfield (Astronomical Calculations)](#skyfield-astronomical-calculations)
    * [Programming Resources & Libraries](#programming-resources-libraries)
    * [Informative Articles & Dates](#informative-articles-dates)
        * [Skyfield Community Discussions](#skyfield-community-discussions)
    * [Visuals](#visuals)
* [Frequent questions](#frequent-questions)
* [Contact and Support](#contact-and-support)
* [Acknowledgments and Credits](#acknowledgments-and-credits)

<!-- vim-markdown-toc -->

## Introduction

   Overview of the software.


### Core Functionalities

- Key features :
- calculation of solar radiation components
  - PV module temperature effect
  - Consideration of system losses

- Common tasks


### Advanced Features

- Using external time series

   Purpose and main features.


### Data Input and Sources

- Information on how to input data into the software
- Details about supported data formats and sources


## Installation

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


## Examples

- Step-by-step examples
- Cover typical and advanced use cases


### CLI

> Too long to document here !

![pvgis-prototype](pvgis-prototype-cli-2023-12-03.png)


### API 

First, run the server:

``` bash
cd pvgisprototype
uvicorn pvgisprototype.webapi:app --reload
```

Then, test some endpoints!

#### Examples

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


### Practical Applications & Tools

#### NREL (National Renewable Energy Laboratory)

- [NREL Solar Radiation Data Manual](https://www.nrel.gov/docs/fy08osti/34302.pdf)

#### NOAA (National Oceanic and Atmospheric Administration)
- [Solar Calculator](https://gml.noaa.gov/grad/solcalc/)
- [AntUV Solar Calculator](https://gml.noaa.gov/grad/antuv/SolarCalc.jsp)
- [Solar Equations PDF](https://gml.noaa.gov/grad/solcalc/solareqns.PDF)
- [Calculation Details](https://gml.noaa.gov/grad/solcalc/calcdetails.html)
- [NOAA Solar Calculator Implementation in Swift](https://github.com/rlxone/SolarNOAA/blob/f044a6ba1ab1e5bdafd0d63d90f134d2192df7f5/Sources/Solar.swift#L286-L308)

#### https://andrewmarsh.com/

> Hands down, one awesome set of resources and interactive applications!

##### Applications

In https://drajmarsh.bitbucket.io/:

- [Interactive Earth-Sun Relationship Tool](https://drajmarsh.bitbucket.io/earthsun.html)
- [2D Sunpath Diagram](https://drajmarsh.bitbucket.io/sunpath2d.html)
- [3D Sunpath Diagram](https://drajmarsh.bitbucket.io/sunpath3d.html)

##### Significant Dates and Times

- [Significant Dates](https://andrewmarsh.com/articles/2019/significant-dates/)
- [Significant Times](https://andrewmarsh.com/articles/2019/significant-times/)

#### Skyfield (Astronomical Calculations)

- Examples : https://rhodesmill.org/skyfield/examples.html#what-time-is-solar-noon-when-the-sun-transits-the-meridian

- Sunrise/Sunset : https://techoverflow.net/2022/06/19/how-to-compute-sunrise-sunset-in-python-using-skyfield/

- UTC and Leap Seconds : https://rhodesmill.org/skyfield/time.html#utc-and-leap-seconds


### Programming Resources & Libraries

**JavaScript**

- [Solar Calculator JavaScript Library](https://unpkg.com/solar-calculator@0.1.0/index.js)
- [NOAA Solar Position Calculator Implementation](https://github.com/mcxsic/noaa-solar-position)

    > Implementation of USA's National Oceanic and Atmospheric Administration
    > (NOAA) Solar Calculator, allowing to find Sunrise, Sunset, Solar Noon and
    > Solar Position for Any Place on Earth.

**R**

- [Photobiology Solar Calculations in R](https://github.com/aphalo/photobiology/blob/HEAD/R/sun.calc.r)

**Ruby**

[Sun - Solar Calculator for Ruby](https://github.com/allspiritseve/sun)

    > Sun is a solar calculator for Ruby based on the National Oceanic &
    > Atmospheric Administration (NOAA) solar calculator. Sunrise and sunset
    > results are apparent times and not actual times (due to atmospheric
    > refraction, apparent sunrise occurs shortly before the sun crosses above the
    > horizon and apparent sunset occurs shortly after the sun crosses below the
    > horizon).


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

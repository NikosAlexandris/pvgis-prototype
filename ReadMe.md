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
    * [Theoretical Background and Scientific Information](#theoretical-background-and-scientific-information)
        * [Wikipedia](#wikipedia)
        * [PV Education](#pv-education)
    * [Practical Applications and Tools](#practical-applications-and-tools)
        * [NOAA](#noaa)
        * [NREL](#nrel)
        * [https://andrewmarsh.com/](#httpsandrewmarshcom)
            * [Applications](#applications)
            * [Resources](#resources)
        * [Skyfield](#skyfield)
        * [Other](#other)
    * [Visuals](#visuals)
* [References](#references)
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

### Theoretical Background and Scientific Information

#### Wikipedia

- https://en.wikipedia.org/wiki/Position_of_the_Sun
- https://en.wikipedia.org/wiki/Equation_of_time

#### PV Education

- https://www.pveducation.org/pvcdrom/properties-of-sunlight/solar-time


### Practical Applications and Tools

#### NOAA

- https://gml.noaa.gov/grad/solcalc/
- https://gml.noaa.gov/grad/antuv/SolarCalc.jsp
- https://gml.noaa.gov/grad/solcalc/solareqns.PDF
- https://gml.noaa.gov/grad/solcalc/calcdetails.html
- https://github.com/rlxone/SolarNOAA/blob/f044a6ba1ab1e5bdafd0d63d90f134d2192df7f5/Sources/Solar.swift#L286-L308

#### NREL

- https://www.nrel.gov/docs/fy08osti/34302.pdf (NREL)

#### https://andrewmarsh.com/

> Hands down, one awesome set of resources and interactive applications!

##### Applications

In https://drajmarsh.bitbucket.io/:

- https://drajmarsh.bitbucket.io/earthsun.html
- https://drajmarsh.bitbucket.io/sunpath2d.html
- https://drajmarsh.bitbucket.io/sunpath3d.html

##### Resources

- https://andrewmarsh.com/articles/2019/significant-dates/
- https://andrewmarsh.com/articles/2019/significant-times/

#### Skyfield

- https://astronomy.stackexchange.com/q/49580/51316
- https://rhodesmill.org/skyfield/examples.html#what-time-is-solar-noon-when-the-sun-transits-the-meridian
- https://techoverflow.net/2022/06/19/how-to-compute-sunrise-sunset-in-python-using-skyfield/
- https://github.com/skyfielders/python-skyfield/discussions/648
- https://rhodesmill.org/skyfield/time.html#utc-and-leap-seconds

**Multi-processing** to Improve performance of sunrise/sunset calculations in
Skyfield

- https://stackoverflow.com/a/69541317/1172302

#### Other

- https://unpkg.com/solar-calculator@0.1.0/index.js
- https://github.com/aphalo/photobiology/blob/HEAD/R/sun.calc.r

- https://github.com/allspiritseve/sun

    > Sun is a solar calculator for Ruby based on the National Oceanic &
    > Atmospheric Administration (NOAA) solar calculator. Sunrise and sunset
    > results are apparent times and not actual times (due to atmospheric
    > refraction, apparent sunrise occurs shortly before the sun crosses above the
    > horizon and apparent sunset occurs shortly after the sun crosses below the
    > horizon).

- https://github.com/mcxsic/noaa-solar-position

    > Implementation of USA's National Oceanic and Atmospheric Administration
    > (NOAA) Solar Calculator, allowing to find Sunrise, Sunset, Solar Noon and
    > Solar Position for Any Place on Earth.

    Implementation of sunrise, sunset and solar noon:

    ``` js
    var times = { sunrise: 0, sunset: 0, solarNoon: 0, state: 'day' };
    times.sunrise = 720 - 4 * (longitude + ha1) - eqTime; // sunrise in minutes at UTC+0
    times.sunrise += cbd.getTimezoneOffsetInMin(); // adjust to timezone, minutes
    times.sunrise *= constants.MINUTES_TO_MILLIS; // convert to millis
    times.sunrise += cbd.getTime(); // convert to millis
    times.sunrise = new Moment(times.sunrise, cbd.getTimezoneOffsetInMin());

    times.sunset = 720 - 4 * (longitude - ha1) - eqTime; // sunset in minutes at UTC+0
    times.sunset += cbd.getTimezoneOffsetInMin(); // adjust to timezone, minutes
    times.sunset *= constants.MINUTES_TO_MILLIS; // convert to millis
    times.sunset += cbd.getTime();
    times.sunset = new Moment(times.sunset, cbd.getTimezoneOffsetInMin());

    times.solarNoon = 720 - 4 * longitude - eqTime; // solar noon in minutes at UTC+0
    times.solarNoon += cbd.getTimezoneOffsetInMin(); // adjust to timezone, minutes
    times.solarNoon *= constants.MINUTES_TO_MILLIS; // convert to millis
    times.solarNoon += cbd.getTime();
    times.solarNoon = new Moment(times.solarNoon, cbd.getTimezoneOffsetInMin());
    ```

### Visuals

-https://niwa.co.nz/our-services/online-services/solarview/solarviewexplanation

## References

..

## Frequent questions

- Common issues users might encounter
- Frequently asked questions with concise answers.

## Contact and Support

- Information on how to get help or support.
- Contact details for reporting bugs or giving feedback.

## Acknowledgments and Credits

- Credit to the EU Commission or any other partners or contributors.
- Acknowledgments of the original PVGIS and its impact.

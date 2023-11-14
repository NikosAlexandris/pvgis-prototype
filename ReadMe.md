# Photovoltaic Information System

## Demonstration

### CLI

> Too long to document here !


### API 

First, run the server:

``` bash
uvicorn pvgisprototype.webapi:app --reload
```

Then, test some endpoints!

#### Examples

##### Solar time

- [`http://localhost:8000/calculate_solar_time_skyfield/?longitude=-70&latitude=40&timestamp=2023-06-26T12:00:00&timezone=America/New_York`](http://localhost:8000/calculate_solar_time_skyfield/?longitude=-70&latitude=40&timestamp=2023-06-26T12:00:00&timezone=America/New_York)

- [`http://localhost:8000/calculate_solar_time_skyfield/?longitude=6.6327&latitude=46.5218&timestamp=2023-06-26T12:04:25&timezone=CET`](http://localhost:8000/calculate_solar_time_skyfield/?longitude=6.6327&latitude=46.5218&timestamp=2023-06-26T12:04:25&timezone=CET)


##### Direct inclined irradiance

- API endpoint to calculate the direct inclined irradiance:

```
..
```

##### Plot solar declination

- [Plot solar declination for 2023](http://localhost:8000/plot_solar_declination_one_year_bokeh?year=2023)


## References

### Solar geometry out there

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

#### NOAA

- https://gml.noaa.gov/grad/solcalc/
- https://gml.noaa.gov/grad/antuv/SolarCalc.jsp
- https://gml.noaa.gov/grad/solcalc/solareqns.PDF
- https://gml.noaa.gov/grad/solcalc/calcdetails.html
- https://github.com/rlxone/SolarNOAA/blob/f044a6ba1ab1e5bdafd0d63d90f134d2192df7f5/Sources/Solar.swift#L286-L308

#### Wikipedia

- https://en.wikipedia.org/wiki/Position_of_the_Sun
- https://en.wikipedia.org/wiki/Equation_of_time

#### NREL

- https://www.nrel.gov/docs/fy08osti/34302.pdf (NREL)


#### Skyfield

- https://astronomy.stackexchange.com/q/49580/51316
- https://rhodesmill.org/skyfield/examples.html#what-time-is-solar-noon-when-the-sun-transits-the-meridian
- https://techoverflow.net/2022/06/19/how-to-compute-sunrise-sunset-in-python-using-skyfield/
- https://github.com/skyfielders/python-skyfield/discussions/648
- https://rhodesmill.org/skyfield/time.html#utc-and-leap-seconds

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
#### PV Education

- https://www.pveducation.org/pvcdrom/properties-of-sunlight/solar-time

### Multi-processing

- https://stackoverflow.com/a/69541317/1172302

### Visuals

-https://niwa.co.nz/our-services/online-services/solarview/solarviewexplanation

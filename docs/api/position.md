---
icon: material/sun-angle
title: Solar Position
subtitle: Estimate photovoltaic performance over a time series based on broadband irradiance
authors:
    - Nikos Alexandris
tags:
  - How-To
  - API
  - Core API
  - Python API
  - Solar Geometry
---

PVGIS features API functions
for each and every elementary solar positioning angle.
To start we launch an interactive `i`/`python` session

``` bash
ipython
```

## Where ?

Define the geographic location and the positioning of our solar surface

```pycon exec="true" session="azimuth-series" source="material-block"
>>> latitude = 45.812
>>> longitude = 8.628
>>> surface_orientation = 177
>>> surface_tilt = 35
```

### Native objects for coordinates

We can also use PVGIS' native classes `Longitude` and `Latitude`
for the coordinates. We can import them as every other Python module
and create objects

```pycon exec="true" session="pvgis-objects" source="material-block"
>>> from pvgisprototype import Longitude, Latitude
```

inspect them

```pycon exec="true" session="pvgis-objects" source="material-block"
>>> longitude = Longitude()
>>> dir(longitude)
```

and use them as in the following example

```pycon exec="true" session="pvgis-objects" source="material-block"
>>> from pvgisprototype import Longitude
>>> Longitude(value=8.628)
>>> longitude = Longitude(value=8.628)
```

Let's see what is in the `longitude` variable

```pycon exec="true" session="pvgis-objects" source="material-block"
    >>> from rich import print
    >>> print(longitude)
```

!!! danger "Incomplete implementation"

    The `Longitude` and `Latitude` data classes are pending some functionality
    such as converting from degrees to radians and vice versa just by calling
    its attribute `.radians` or `.degrees`. Such methods will make it easier to
    write programs on top of PVGIS and not only.

## When ?

Prepate a series of timestamps as a Pandas DatetimeIndex,
using _our_ helper function `generate_datetime_series`

```pycon exec="true" session="azimuth-series" source="material-block"
>>> from pvgisprototype.api.datetime.datetimeindex import generate_datetime_series

>>> timestamps = generate_datetime_series(start_time="2010-01-27 08:00:00", end_time="2010-01-27 18:00:00", frequency="h")
```

and the default UTC timezone as a `ZoneInfo` object

```pycon exec="true" session="azimuth-series" source="material-block"
>>> from zoneinfo import ZoneInfo

>>> utc_zone = ZoneInfo("UTC")
```

Let's confirm the generation of the timestamps and the timezone :

```pycon exec="true" session="azimuth-series" source="material-block"
>>> print(f'{timestamps=}')
>>> print(f'\n{utc_zone=}')
```

## Solar altitude

``` pycon exec="1" source="console" session="solar-altitude"
>>> from pvgisprototype.api.position.altitude import calculate_solar_altitude_series
>>> calculate_solar_altitude_series
```

<!-- ``` python exec="1" source="console" session="solar-altitude" -->
<!-- helptext = help(calculate_solar_altitude) -->
<!-- print(helptext) -->
<!-- ``` -->

We can see the required arguments to run the command

## Error Handling

Let's give it a first try with some _reasonable_ input values for `longitude`,
`latitude` and `timestamps` plus `timezone`

!!! failure

    ``` pycon exec="1" source="console" session="solar-altitude"
    >>> calculate_solar_altitude_series(8, 45, '2001-01-01 10:00:00', 'UTC')
    ```

PVGIS' API is indeed idiomatic and our _reasonable_ inputs won't work !
However,
the input arguments are validated via Pydantic
and thus we receive informative error messages.

## Speaking PVGIS' API language

Let's import the required modules

```pycon exec="1" source="console" session="solar-altitude"
>>> from pandas import Timestamp
>>> from zoneinfo import ZoneInfo
>>> from pvgisprototype.api.utilities.conversions import convert_float_to_radians_if_requested
```

Setting the input parameters

```pycon exec="1" source="console" session="solar-altitude"
>>> latitude=convert_float_to_radians_if_requested(8, 'radians')
>>> longitude=convert_float_to_radians_if_requested(45, 'radians')
>>> timestamps=Timestamp('2001-01-01 10:00:00+00:00')
>>> timezone=ZoneInfo('UTC')
```

And re-run the calculation

```pycon exec="1" source="console" session="solar-altitude"
>>> solar_altitude = calculate_solar_altitude_series(longitude=longitude, latitude=latitude, timestamps=timestamps, timezone=timezone)
>>> print(f"Solar altitude from PVGIS' API : {solar_altitude}")
```

## :material-sun-compass: Solar Azimuth

We can calculate solar azimuth angles
for a specific geographic location and over a time series
with the API function `calculate_solar_azimuth_series()`.

```pycon exec="true" session="azimuth-series" source="material-block"
>>> from pvgisprototype.api.position.azimuth import calculate_solar_azimuth_series
```

### Help

What exactly can we do with it ?
We can use the Python built-in function `help` to find out

``` python
>>> help(calculate_solar_azimuth_series)
```

Or indeed, in an interactive ipython session, it suffices to use a `?` right
after the function name and without space

```python
>>> calculate_solar_azimuth_series?
```

### More Imports

```pycon exec="true" session="azimuth-series" source="material-block"
>>> from math import radians
>>> from pvgisprototype.api.datetime.datetimeindex import generate_datetime_series
>>> timestamps = generate_datetime_series(start_time='2010-01-27', end_time='2010-01-28')
>>> from zoneinfo import ZoneInfo
```

Calculate solar azimuth time series for the 27th January 2010 

```pycon exec="true" session="azimuth-series" source="material-block"
>>> calculate_solar_azimuth_series(
... longitude=radians(longitude),
... latitude=radians(latitude),
... timestamps=timestamps,
... timezone=ZoneInfo("UTC"),
... adjust_for_atmospheric_refraction=True
... )
```

The above command returns a PVGIS-native data class `SolarAzimuth`.
Of course we can feed the result to a new variable
and print or re-use it for further processing

```pycon exec="true" session="azimuth-series" source="material-block"
>>> solar_azimuth_series = calculate_solar_azimuth_series(
... longitude=radians(longitude),
... latitude=radians(latitude),
... timestamps=timestamps,
... timezone=ZoneInfo("UTC"),
... adjust_for_atmospheric_refraction=True
... )
>>> print(solar_azimuth_series)
```

!!! danger "Yet to implement!"

    !!! tip "Convert output to degrees"

        Note, most PVGIS data classes feature a standard `.degrees` method
        -- it'll convert the values to geographic degrees :

        ```pycon exec="true" session="azimuth-series" source="material-block"
            >>> from rich import print
            >>> print(solar_azimuth_series.degrees)
        ```

---
icon: material/sun-angle
title: Solar Position
subtitle: Estimate photovoltaic performance over a time series based on broadband irradiance
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

We can also use PVGIS' native classes for the coordinates

```pycon exec="true" session="pvgis-objects" source="material-block"
from pvgisprototype import Longitude, Latitude
```

and 

```pycon exec="true" session="pvgis-objects" source="material-block"
>>> from pvgisprototype import Longitude
>>> Longitude(value=8.628)
>>> longitude = Longitude(value=8.628)
```

```pycon exec="true" session="pvgis-objects" source="material-block"
>>> print(longitude)
```

## When ?

Prepate a series of timestamps as a Pandas DatetimeIndex,
using _our_ helper function `generate_datetime_series`

```pycon exec="true" session="azimuth-series" source="material-block"
>>> from pvgisprototype.api.utilities.timestamp import generate_datetime_series

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

## Solar Azimuth

We can calculate solar azimuth angles
for a specific geographic location and over a time series
with the API function `calculate_solar_azimuth_time_series_noaa()`.

```pycon exec="true" session="azimuth-series" source="material-block"
>>> from pvgisprototype.api.position.azimuth_series import calculate_solar_azimuth_time_series_noaa
```

### Help

What exactly can we do with it ?
We can use the Python built-in function `help` to find out

``` python
>>> help(calculate_solar_azimuth_time_series_noaa)
```

Or indeed, in an interactive ipython session, it suffices to use a `?` right
after the function name and without space

```python
>>> calculate_solar_azimuth_time_series_noaa?
```

### More Imports

```pycon exec="true" session="azimuth-series" source="material-block"
>>> from math import radians
>>> from pvgisprototype.api.utilities.timestamp import generate_datetime_series
>>> timestamps = generate_datetime_series(start_time='2010-01-27', end_time='2010-01-28')
>>> from zoneinfo import ZoneInfo
```

Calculate solar azimuth time series for the 27th January 2010 

```pycon exec="true" session="azimuth-series" source="material-block"
>>> calculate_solar_azimuth_time_series_noaa(
... longitude=radians(longitude),
... latitude=radians(latitude),
... surface_orientation=radians(surface_orientation),
... surface_tilt=radians(surface_tilt),
... timestamps=timestamps,
... timezone=ZoneInfo("UTC"),
... apply_atmospheric_refraction=True
... )
```

The above command returns a PVGIS-native data class `SolarAzimuth`.
Of course we can feed the result to a new variable
and print or re-use it for further processing

```pycon exec="true" session="azimuth-series" source="material-block"
>>> solar_azimuth_series = calculate_solar_azimuth_time_series_noaa(
... longitude=radians(longitude),
... latitude=radians(latitude),
... surface_orientation=radians(surface_orientation),
... surface_tilt=radians(surface_tilt),
... timestamps=timestamps,
... timezone=ZoneInfo("UTC"),
... apply_atmospheric_refraction=True
... )
>>> print(solar_azimuth_series)
```

!!! tip "Convert output to degrees"

    Note, most PVGIS data classes feature a standard `.degrees` method
    -- it'll convert the values to geographic degrees :

    ```pycon exec="true" session="azimuth-series" source="material-block"
    >>> print(solar_azimuth_series.degrees)
    ```

---
icon: material/language-python
title: How-To
summary: How to use the API
authors:
    - Nikos Alexandris
tags:
  - API
  - Core API
  - Python API
  - Example
---

```pycon exec="1" source="console" session="pvgis-location"
>>> from pvgisprototype import Longitude, Latitude
```
and

```pycon exec="1" source="console" session="pvgis-location"
>>> longitude = Longitude()
>>> dir(longitude)
>>> print(longitude)
```

``` pycon exec="1"
>>> from pvgisprototype import Longitude
>>> print(Longitude)
>>> print(Longitude())
>>> Longitude()
```

```python exec="1"
from pvgisprototype import Longitude
Longitude()
```

## Solar altitude

``` pycon exec="1" source="console" session="solar-altitude"
>>> from pvgisprototype.api.geometry.altitude import calculate_solar_altitude
>>> calculate_solar_altitude
```

<!-- ``` python exec="1" source="console" session="solar-altitude" -->
<!-- helptext = help(calculate_solar_altitude) -->
<!-- print(helptext) -->
<!-- ``` -->

We can see the required arguments to run the command

## Error Handling

Let's give it a first try with some _reasonable_ inputs

!!! failure

    ``` pycon exec="1" source="console" session="solar-altitude"
    >>> calculate_solar_altitude(8, 45, '2001-01-01 10:00:00', 'UTC')
    ```

PVGIS' API is indeed idiomatic and our _reasonable_ inputs won't work.
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

And retry again

```pycon exec="1" source="console" session="solar-altitude"
>>> solar_altitude = calculate_solar_altitude(convert_float_to_radians_if_requested(8, 'radians'), convert_float_to_radians_if_requested(45, 'radians'), Timestamp('2001-01-01 10:00:00+00:00'), ZoneInfo('UTC'))
>>> print(f"Solar altitude from PVGIS' API : {solar_altitude}")
```

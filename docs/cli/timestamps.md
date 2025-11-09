---
icon: material/calendar-clock
description: How to work with time series
title: Timestamps
subtitle: Work with time series
tags:
  - How-To
  - CLI
  - Time Series
  - Timestamps
---

## Overview

<div class="grid cards" markdown>

- :simple-pandas: __Supported by Pandas__

    - Arbitrary time series supported by [Pandas' DatetimeIndex](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html)
    - Relevant input parameters : `start_time`, `end_time`, `periods` and  `frequency`.

    !!! note

        Learn more about frequency strings at [Offset aliases](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases).


- :material-map-clock: __[IANA Time Zone Database](https://www.iana.org/time-zones)__

    - Support for valid time zone identifiers from [the IANA Time Zone Database](https://www.iana.org/time-zones)


- __Defaults__

    !!! danger "Attention!"

        - If not given, default time is `00:00:00`. No solar irradiance at this time ! 

        - `UTC` is the default timezone in which internal calculations are performed anyway.

        - Frequency of timestamps is unrelated to the `groupby` option !


- :material-console-line: __Working examples__

    !!! example

        - Examples that should just work

</div>

PVGIS relies on the excellent _timestamping_ engine of [Pandas][pandas].

[pandas]: https://pandas.pydata.org/

We can use all of the flexibility to build almost any kind of series of
timestamps!

## Optional parameters

The basic entrypoint for timestamp/s is the positional argument `timestamps`.
Notwithstanding,
a series of optional input parameters offer the flexibility to generate custom
series of timestamps. These are :

- `--start-time` : a starting timestamp
- `--end-time` : an ending timestamp
- `--periods` : the number of timestamps within a time range starting with the
  `start_time` and ending with the `end_time` timestamp.
- `--frequency` :

!!! note "Source code of..."

    **Update-Me**

## Examples

### Local time and zone

Interested for the photovoltaic power output at your current local time and zone ?
Just ommit the timestamp altogether !

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8 45 214 -v
```

!!! tip "Using the system's current time and zone!"

    The above example expectedly picked up the time and zone of the virtual
    computer on which this very page has been build after some change commited
    in the source code tree!


!!! danger "Missing positional parameters?"

    Remember, a specific user-defined timestamp, or list of timestamps
    separated by comma for the matter, would fail due to absence of _all_
    required positional arguments, i.e. :

    ``` bash exec="true" result="ansi" source="material-block" returncode="1"
    pvgis-prototype power broadband 8 45 214 '2010-01-27 12:00:00'
    ```

### Start and end dates

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8 45 214 180 45 --start-time '2010-01-27' --end-time '2010-01-28'
```

### Start and end date-times

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8 45 214 180 45 --start-time '2010-01-27 06:00:00' --end-time '2010-01-28 17:30:00' -v
```

### Frequency

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8 45 214 180 45 --start-time '2010-01-27 06:00:00' --end-time '2010-01-28 17:30:00' --frequency 30min -v
```

### Number of periods

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8 45 214 180 45 --start-time '2010-01-27 06:00:00' --end-time '2010-01-28 17:30:00' --periods 8 -v
```
### With Orientation and Tilt

We can define the specific orientation and tilt angles, right after the
location coordinates and the elevation :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8 45 214 167 44 --start-time '2010-01-27 06:00:00' --end-time '2010-01-28 17:30:00' --periods 8 -v
```
### With Orientation only

Or only the orientation.

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8 45 214 167 --start-time '2010-01-27 06:00:00' --end-time '2010-01-28 17:30:00' --periods 8 -v
```

!!! warning "Tilt ?"

    It is impossible at the moment to re-define the tilt angle only, without
    preceeding it by an orientation angle.

---
icon: material/sun-clock
description: How to work with time series
title: Timestamps
subtitle: Learn how to work with time series
tags:
  - How-To
  - CLI
  - Time Series
  - Timestamps
---

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

!!! seealso "Source code of..."

    **Update-Me**

## Examples

### Local time and zone

Interested for the photovoltaic power output at your Local time and zone ?
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
pvgis-prototype power broadband 8 45 214 --start-time '2010-01-27' --end-time '2010-01-28'
```

### Start and end date-times

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8 45 214 --start-time '2010-01-27 06:00:00' --end-time '2010-01-28 17:30:00' -v
```

### Frequency

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8 45 214 --start-time '2010-01-27 06:00:00' --end-time '2010-01-28 17:30:00' --frequency 30min -v
```

### Number of periods

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8 45 214 --start-time '2010-01-27 06:00:00' --end-time '2010-01-28 17:30:00' --periods 8 -v
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

### Quiet (a) long time series

Printing very long time series in the terminal is rather impractical,
aside that it takes quite some time for the print-out. To work-around this
limitation, there is a `--quiet` optional flag which will ommit the print out.

This option may be useful for timing the duration of processes or printing a
plot of the output or metadata of the command itself.

### Duration of command execution

We can _time_ the duration of a command that processes a long time series using
the terminal's built-in function `time` :

``` bash exec="true" result="ansi" source="material-block"
time pvgis-prototype power broadband 8 45 214 167 --start-time '2000-01-01' --end-time '2020-12-31' --quiet
```

### Plot of output time series

We can _time_ the duration of a command that processes a long time series using
the terminal's built-in function `time` :

``` bash exec="true" result="ansi" source="material-block"
time pvgis-prototype power broadband 8 45 214 167 --start-time '2000-01-01' --end-time '2020-12-31' --quiet --uniplot
```

### Fingerprint of output time series

We can _time_ the duration of a command that processes a long time series using
the terminal's built-in function `time` :

``` bash exec="true" result="ansi" source="material-block"
time pvgis-prototype power broadband 8 45 214 167 --start-time '2000-01-01' --end-time '2020-12-31' --quiet --fingerprint
```

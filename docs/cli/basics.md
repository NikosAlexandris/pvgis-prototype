---
icon: material/alphabetical
description: Introduction to the basic CLI structure
title: Basics
subtitle: Learn how to work with PVGIS interactively
tags:
  - How-To
  - CLI
---

!!! info "Overview"

    This section introduces the basic structure of the command line interface,
    various commands, required arguments and optional parameters
    as well as some insight into generating arbitrary series of Timestamps.

The fundamental structure of the command line interface is
a `command`
_following_ the name of the program `pvgis-prototype`
and a series of _required_ and _optional_ input parameters.
Like so :

```bash
pvgis-prototype <command> <1> <2> <3> <--option-a 'a'> <--option-b 'b'>
```

## Command Structure

With a few exceptions,
the `power`, `irradiance` and `position` commands,
require _at the very least_
the three basic input parameters
that describe the **location of a solar surface**.
Hence a more descriptive representation of basic command structure is :

``` bash
pvgis-prototype <command> <Longitude> <Latitude> <Elevation>
```

## Orientation and Tilt

What follows after the location parameters
is the **pair of `orientation` and `tilt` angles**
of the solar surface in question.

``` bash
pvgis-prototype <command> <Longitude> <Latitude> <Elevation> <Orientation> <Tilt>
```

If not provided,
the default pre-set values are `orientation = 180` and `tilt = 45` degrees.

## Time

Of course,
_time_ is the first variable that determines the position of the sun in the sky
and therefore impacts each and every calculation that depends on it.
Nonetheless, in PVGIS, it comes as the last required positional parameter!
The importance of _time_ is such that we have a dedicated section called
[Timestamps](cli/timestamps.md) !

``` bash
pvgis-prototype <command> <Longitude> <Latitude> <Elevation> <Orientation> <Tilt> <Timestamp>
```

!!! tip "The default timestamp is your computer's current time and local zone!"

    However, for the sake of ease of use and practice,
    if not given,
    the `timestamp`/`s` is set form your system's current local time and zone.

!!! attention

    If a specific timestamp or series of timestamps are given,
    then **all required input arguments are expected to be given**.
    Missing one of the positional required parameters will cause the program to
    exit with an error message asking for the _next_ missing input parameter.
    See following examples.

## Examples that work

Example that works with all positional parameters yet without a timestamp:

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 170 44
```

Example that works with all positional parameters including a timestamp:

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 170 44 '2010-01-27 12:00:00'
```

Example that works with all positional parameters including multiple timestamps:

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 170 44 '2010-01-27 12:00:00, 2010-01-27 13:30:00, 2010-01-27 17:45:00'
```

The same as above, with additional verbosity : 

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 170 44 '2010-01-27 12:00:00, 2010-01-27 13:30:00, 2010-01-27 17:45:00' -v
```

## Examples that fail !

Example that fails :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 170 '2010-01-27 12:00:00'
```

!!! danger

    In the above example, the surface tilt angle is missing, followed by a
    user-requested timestamp. Due to the nature of the command line positional
    arguments, it is expected to follow strictly their order.

Another example that fails :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 44 '2010-01-27 12:00:00'
```

!!! danger

    In the above example, the surface orientation angle is missing,
    followed by a user-requested timestamp.

One more example that fails :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 '2010-01-27 12:00:00'
```

!!! danger

    In the last example that fails,
    both the surface orientation angle and tilt angles are missing followed by
    a user-requested timestamp.

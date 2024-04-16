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

## Generic Structure

The fundamental structure of the command line interface is
a `command`
_following_ the name of the program **`pvgis-prototype`**
and a series of _required positional_, _optional positional_
and _named optional_ input parameters. Like so :

```bash
pvgis-prototype <command> <1> <2> <3> [4] [5] <--option-a 'a'> <--option-b 'b'>
```

### Positional parameters

- The numbers `<1>`, `<2>` and `<3>` enumerate the ***required*** _positional_ parameters.
- The numbers `[4]` and `[5]` enumerate are ***optional*** positional_ parameters.

Positional parameters need no prefixing.
However,
they are required to be given strictly in the pre-specified order.

### Optional parameters

Optional parameters need

1. to be _named_, for example `--verbose` or its equivalent simpler form
  `-v`.
2. **not** to be given in a specific order, i.e. asking for `-v --uniplot` is
   the same as `--uniplot -v`.


### Location

With a few exceptions,
the `power`, `irradiance` and `position` commands,
require _at the very least_
the three basic input parameters
that describe the **location of a solar surface**.
Hence a more descriptive representation of the basic command structure is :

``` bash
pvgis-prototype <command> <Longitude> <Latitude> <Elevation>
```

### Orientation and Tilt

What follows after the location parameters
is the **pair of `orientation` and `tilt` angles**
of the solar surface in question.

``` bash
pvgis-prototype <command> <Longitude> <Latitude> <Elevation> <Orientation> <Tilt>
```

If not provided,
the default pre-set values are `orientation = 180` and `tilt = 45` degrees.

### Time

Of course,
_time_ is the first variable that determines the position of the sun in the sky
and therefore impacts each and every calculation that depends on it.
Nonetheless, in PVGIS, it comes as the last required positional parameter!
The importance of _time_ is such that we have a dedicated section called
[Timestamps](timestamps.md) !

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

### Without a timestamp

Example that works with all positional parameters yet without a timestamp:

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 170 44
```

As mentioned above, this command will run with your computer's current local time and zone. We can see for example which timestamp the command ran for by adding some verbosity :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 170 44 -v
```

### For a single timestamp

Example that works with all positional parameters including a timestamp:

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 170 44 '2010-01-27 12:00:00'
```

### For an arbitrary number of single timestamps

Example that works with all positional parameters including multiple timestamps:

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 170 44 '2010-01-27 12:00:00, 2010-01-27 13:30:00, 2010-01-27 17:45:00'
```

The same as above, with additional verbosity : 

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 170 44 '2010-01-27 12:00:00, 2010-01-27 13:30:00, 2010-01-27 17:45:00' -v
```

### Mixing optional parameters

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 170 44 '2010-01-27 12:00:00, 2010-01-27 13:30:00, 2010-01-27 17:45:00' -v --quiet --uniplot
```

is the same as

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 170 44 '2010-01-27 12:00:00, 2010-01-27 13:30:00, 2010-01-27 17:45:00' --quiet --uniplot --verbose
```

## Examples that fail !

It is useful to get a sense of things that don't work too.
Following are some examples that fail
and ideally should return meaninfgul error messages.

!!! danger

    Example that fails :

    ``` bash exec="true" result="ansi" source="material-block"
    pvgis-prototype irradiance global inclined 8 45 214 170 '2010-01-27 12:00:00'
    ```

    In the above example, the surface tilt angle is missing, followed by a
    user-requested timestamp. Due to the nature of the command line positional
    arguments, it is expected to follow strictly their order.

!!! danger

    Another example that fails :

    ``` bash exec="true" result="ansi" source="material-block"
    pvgis-prototype irradiance global inclined 8 45 214 44 '2010-01-27 12:00:00'
    ```

    In the above example, the surface orientation angle is missing,
    followed by a user-requested timestamp.

!!! danger

    One more example that fails :

    ``` bash exec="true" result="ansi" source="material-block"
    pvgis-prototype irradiance global inclined 8 45 214 '2010-01-27 12:00:00'
    ```

    In the last example that fails,
    both the surface orientation angle and tilt angles are missing followed by
    a user-requested timestamp.

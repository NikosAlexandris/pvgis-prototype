---
icon: material/alphabetical
description: Introduction to the basic CLI structure
title: Basics
subtitle: Basics of the Command Line Interface
tags:
  - How-To
  - CLI
---

## Overview

This section introduces the basic structure of the command line interface,
various commands, required arguments and optional parameters
as well as some insight into generating arbitrary series of Timestamps.

<div class="grid cards" markdown>

- :material-at: __Generic structure__

    ---

    ``` bash
    pvgis-prototype \
        <command> \
        <sub-command> \
        <sub-sub-command> \
        <1> <2> <3> \
        [4] [5] \
        <--option-a 'a'> \
        <--option-b 'b'> \
        ..
    ```

- :material-puzzle-plus: __Positional parameters__

    - No prefixing

    - Strict order

    - `<1>`, `<2>` and `<3>` are ***required***  
      for <Longitude> <Latitude> <Elevation>

    - `[4]` and `[5]` are ***optional***  
      for [Orientation] and [Tilt]


- :material-console-line: __Working examples__

    !!! example
        
        - Examples that should just work


- :material-console-line: __Examples that fail__

    !!! danger
        
        - Examples that fail so we know it is no-one's fault!

</div>


## Generic Structure

The fundamental structure of the command line interface is
a `command` and a `sub-command`
_following_ the name of the program **`pvgis-prototype`**
and a series of __required__ _positional_, __optional__ _positional_
and __named__ _optional_ input parameters. Like so :

```bash
pvgis-prototype <command> <sub-command> \
    <1> <2> <3> \
    [4] [5] \
    <--option-a 'a'> <--option-b 'b'>
```

!!! example

    ``` bash
    pvgis-prototype power broadband 8 45 214 170 44
    ```

    where :

    - `power` is the command
    - `broadband` a sub-command
    - `8 45` are the Longitude and Latitude
    - `214` is the Elevation
    - `170 44` are the Orientation and Tilt angles

Several commands feature chained `sub-sub-commands`.
The structure remains the same and a `sub-command` `sub-sub-command`
only add up to the `command`
which indeed follows the generic program name **`pvgis-prototype`** like

``` bash
pvgis-prototype \
    <command> \
    <sub-command> \
    <sub-sub-command> \
    <1> <2> <3> [4] [5] \
    <--option-a 'a'> \
    <--option-b 'b'> \
    ..
```

!!! example

    To calculate the global _horizontal_ irradiance
    at our example location and at '2010-01-27 12:00:00' we can do

    ``` bash
    pvgis-prototype irradiance global horizontal 8 45 214 '2010-01-27 12:00:00'
    ```

    For clarity,
    let's look at the command's parts written out one part per line

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype \
        irradiance \
        global \
        horizontal \
        8 45 214 \
        '2010-01-27 12:00:00'
    ```
    
    where :

    - `irradiance` is the command
    - `global` a sub-command
    - `horizontal` a sub-sub-command
    - `8 45 214` the Longitude, Latitude and Elevation
    - '2010-01-27 12:00:00' the requested timestamp

!!! example

    We can calculate the global _inclined_ irradiance at our example location
    and at '2010-01-27 12:00:00' via

    ``` bash
    pvgis-prototype irradiance global inclined 8 45 214 170 44 '2010-01-27 12:00:00'
    ```

    For clarity,
    let's look at the command's parts written out one part per line

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype \
        irradiance \
        global \
        inclined \
        8 45 214 170 44 \
        '2010-01-27 12:00:00'
    ```
    
    where :

    - `irradiance` is the command
    - `global` a sub-command
    - `inclined` a sub-sub-command
    - `8 45 214 170 44` the Longitude, Latitude, Elevation, surface Orientation
      and surface Tilt
    - '2010-01-27 12:00:00' the requested timestamp

### Positional parameters

- The numbers `<1>`, `<2>` and `<3>` enumerate the ***required*** _positional_ parameters.
- The numbers `[4]` and `[5]` enumerate two ***optional*** yet _positional_ parameters.
- Positional parameters need no prefixing. However, they are required to be
  given strictly in the pre-specified order.

### Optional parameters

Optional parameters need

1. to be _named_, for example [`--verbose`](verbosity) or its equivalent
   simpler form `-v`.

2. **not** to be given in a specific order, i.e. asking for `-v --uniplot` is
   the same as `--uniplot -v`.

### Location

With a few exceptions,
the `performance`, `power`, `irradiance` and `position` commands,
require _at the very least_
the three basic input parameters
that describe the **location of a solar surface**.
A more descriptive representation of the basic command structure is :

``` bash
pvgis-prototype <command> <Longitude> <Latitude> <Elevation>
```

### Orientation and Tilt

What follows after the location parameters
is the **pair of `orientation` and `tilt` angles**
of the solar surface in question.

``` bash
pvgis-prototype <command> <Longitude> <Latitude> <Elevation> [Orientation] [Tilt]
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

Example that works with all positional parameters yet _without_ a timestamp :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 170 44
```

As mentioned above,
this command will run with your computer's current local time and zone.
We can see for example which timestamp the command ran for
by adding some verbosity :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 170 44 -v
```

!!! question "Where did this timestamp came from ?"

    The timestamp in the above command
    is the one of this very example's execution time
    which ran at build time of the interactive documentation you are reading.

### Single timestamp

Example that works with all positional parameters _including_ a timestamp:

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined \
    8 45 214 170 44 \
    '2010-01-27 12:00:00'
```

### Arbitrary number of single timestamps

Example that works with all positional parameters including multiple timestamps:

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined \
    8 45 214 170 44 \
    '2010-01-27 12:00:00, 2010-01-27 13:30:00, 2010-01-27 17:45:00'
```

The same as above, with additional verbosity : 

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 214 170 44 '2010-01-27 12:00:00, 2010-01-27 13:30:00, 2010-01-27 17:45:00' -v
```

### Mixing optional parameters

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined \
    8 45 214 170 44 \
    '2010-01-27 12:00:00, 2010-01-27 13:30:00, 2010-01-27 17:45:00' \
    -v \
    --quiet
```

is the same as

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined \
    8 45 214 170 44 \
    '2010-01-27 12:00:00, 2010-01-27 13:30:00, 2010-01-27 17:45:00' \
    --quiet \
    --verbose
```

One more example _mixing_ the order of options

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined \
    8 45 214 170 44 \
    '2010-01-27 12:00:00, 2010-01-27 13:30:00' \
    -v \
    --quiet \
    -vv
```

!!! warning "--quiet silences the output"

    All of the above commands will not return anything since this is what the
    `--quiet` flag (or `-q` for the matter) is meant to do!

## Examples that fail !

It is useful to get a sense of things that _don't work_ too.
Following are some examples that fail
and ideally should return meaninfgul error messages.

!!! danger "Example that fails"

    ``` bash
    pvgis-prototype irradiance global inclined 8 45 214 170 '2010-01-27 12:00:00'
    ```

    ``` bash exec="true" result="ansi"
    pvgis-prototype irradiance global inclined 8 45 214 170 '2010-01-27 12:00:00' # markdown-exec: hide
    ```

    In the above example, the surface tilt angle is missing, followed by a
    user-requested timestamp. Due to the nature of the command line positional
    arguments, it is expected to follow strictly their order.

!!! danger "Another failing example"

    ``` bash
    pvgis-prototype irradiance global inclined 8 45 214 44 '2010-01-27 12:00:00'
    ```

    ``` bash exec="true" result="ansi" source="material-block"
    pvgis-prototype irradiance global inclined 8 45 214 44 '2010-01-27 12:00:00'
    ```

    In the above example, the surface orientation angle is missing,
    followed by a user-requested timestamp.

!!! danger "One more failing example"

    ``` bash
    pvgis-prototype irradiance global inclined 8 45 214 '2010-01-27 12:00:00'
    ```

    ``` bash exec="true" result="ansi" source="material-block"
    pvgis-prototype irradiance global inclined 8 45 214 '2010-01-27 12:00:00'
    ```

    In the last failing example,
    both the surface _orientation_ and _tilt_ angles are missing followed by
    a user-requested _timestamp_.

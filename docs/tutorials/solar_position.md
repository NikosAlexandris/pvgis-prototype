---
icon: material/sun-angle
title: Solar Position
tags:
  - Tutorial
  - CLI
  - Solar Geometry
---

# Location & Panel Geometry

To begin with,
let's define the fundamental input parameters for our location of interest and
a moment in time :

- Location : (Lon, Lat) = (**8**, **45**)
- Elevation : **214 m**
- A good, clear-sky day over our location is `2010-01-27 12:00:00`.

Next, let us consider the basic _geometry_ of a solar panel :

- Orientation of the panel : **South** which is **180 degrees** counting clock-wise
  from due North.
- Tilt of the Panel : **a horizontally flat panel** which is **0 degrees**.

!!! note "Symbols"
 
    - The ∡ symbol means we are reporting an inclined component!
    - The calculations include the atmospheric refraction (as described in Hofierka, 2002)
    - The albedo is set to 0.2
    - The Linke Turbidity is set to 2
 
!!! warning "On the Linke Turbidity"

    By default, PVGIS does _not_ use any Linke Turbidity input
    when it gets to read solar irradiance components from external datasets,
    such as for example SARAH3 products.

    *EXPLAIN HERE MORE*

# Solar position

As a starting point,
the command `position`,
features a sub-command `introduction`
which returns a text
explaining the flow of calculations of the position of the sun
and the agle between sun-rays and the solar collector surface.

Go ahead, try it out and skim through the text !

``` bash
pvgis-prototype position introduction
```

!!! note

    Refer to the [introduction to solar position](../cli/position/introduction.md)
    how-to section.

Now that we have an overview,
let's start with the basics :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype position overview \
    8.628 45.812 180 45 \
    '2010-01-17 12:00' \
    -aou degrees
```

!!! info

    **The command**
    
    ``` bash
    pvgis-prototype position overview \
    8.628 45.812 180 45 \
    '2010-01-17 12:00' \
    -aou degrees
    ```

    **reads** :

    - execute `pvgis-prototype` command `position` and sub-command `overview`
    - set
        - the longitude to `8.628` and the latitude to `45.812`
        - the surface (panel) orientation to `180` and the tilt to `45` degrees
        - the timestamp `2010-01-17 12:00`
    - output the angle quantities in `degrees`

!!! warning "Degrees or radians ?"

    By default, PVGIS returns angle figures measured in radians. This extra bit
    of `-aou` which is a shortcut for `--angle-output-units`
    is required to get the reported numbers in degrees. Without it :

    ``` bash exec="true" result="ansi" source="material-block"
    pvgis-prototype position overview \
    8.628 45.812 180 45 \
    '2010-01-17 12:00'
    ```

    Let's note down the solar zenith angle (in radians) : **1.16802**

## Altitude and Azimuth

The two solar position angles of interest initially are
the **solar altitude** (also referred to as solar elevation)
and the **solar azimuth**.

We can identify them individually :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype position altitude \
    8.628 45.812 \
    '2010-01-17 12:00:00' \
    -aou degrees
```

and

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype position azimuth \
    8.628 45.812 \
    '2010-01-17 12:00:00' \
    -aou degrees \
    --solar-position-model noaa
```

# Incidence angle

Nonetheless,
the single-most important angle in the context of photovoltaics,
is the solar incidence angle.
Let's get it for a South-facing surface,
tilted at 35 degrees

``` bash exec="true" result="ansi" source="material-block" hl_lines="3"
pvgis-prototype position incidence \
    8.628 45.812 \
    180 35 \
    '2010-01-17 12:00:00' \
    -aou degrees
```

!!! warning Orientation & Tilt angles

    The `incidence` command requires a surface orientation and tilt angle (see
    highlighted figures in the above example).
    Missing to provide these parameters, would cause the command to fail.

<!-- returns -->
<!--   Time                  Declination ∢   Hour Angle 🕛   Zenith ⦭   Altitude ⦩   Azimuth ⭮   Incidence ⦡ -->
<!--  ─────────────────────────────────────────────────────────────────────────────────────────────────────── -->
<!--   2010-01-17 12:00:00   -20.9036        6.29694         66.92272   23.07728     174.11928   68.9886 -->

<!-- Position  Longitude ϑ, Latitude ϕ = 8.62800, 45.81200, Orientation : 180.00000, Tilt : 45.00000 [degrees] -->
<!--      Algorithms  Timing : NOAA, Zone : UTC, Local zone : UTC, Positioning : NOAA, Incidence angle : -->
<!--                                               Sun-to-Plane -->

The solar radiation model presented by Hofierka (2002),
defines as _solar incidence_
{==the angle between the sun-rays and the **plane** of the solar surface==}.
Or else : the angle between the position of the sun and the inclination of the
panel.

Typically,
_solar incidence_ is defined as
{==the angle between the sun-rays and the **normal** to the reference surface==}.
It is important to disinguish between the two, hence,
in PVGIS we call the _Sun-To-Plane_ the _complementary_ incidence angle,
where as the _Sun-to-Surface-Normal_
we call it the _typical_ incidence angle.

To get the _typical_ solar incidence angle,
one can use the optional flag `--sun-vector-to-surface-normal`
(or even `--sun-to-normal`) like so :

``` bash exec="true" result="ansi" source="material-block" hl_lines="5"
pvgis-prototype position overview \
    8.628 45.812 180 45 \
    '2010-01-17 12:00' \
    -aou degrees \
    --sun-vector-to-surface-normal
```

# Time series

The power of `overview`
is exactly its capability to generate time series.

It suffices to provide a `start-time` and an `end-time` :

``` bash exec="true" result="ansi" source="material-block" hl_lines="3 4"
pvgis-prototype position overview \
    8.628 45.812 180 45 \
    --start-time '2010-01-17 06:00:00' \
    --end-time '2010-01-17 18:00:00' \
    -aou degrees
```

And what about every 30 minutes ?
Ask this via the `--frequency` option :

``` bash exec="true" result="ansi" source="material-block" hl_lines="6"
pvgis-prototype position overview \
    8.628 45.812 180 45 \
    --start-time '2010-01-17 06:00:00' \
    --end-time '2010-01-17 18:00:00' \
    -aou degrees \
    --frequency 30min
```

Maybe we want shorter figures ?
We can limit the output numbers to 2 decimals :

``` bash exec="true" result="ansi" source="material-block" hl_lines="6"
pvgis-prototype position overview \
    8.628 45.812 180 45 \
    --start-time '2010-01-17 06:00:00' \
    --end-time '2010-01-17 18:00:00' \
    -aou degrees \
    -r 2
```

# Uniplot

We can also have just a visual overview via the `--uniplot` option
along with `--quiet` to hide the tabular output :

``` bash exec="true" result="ansi" source="material-block" hl_lines="7"
pvgis-prototype position overview \
    8.628 45.812 180 45 \
    --start-time '2010-01-17 06:00:00' \
    --end-time '2010-01-17 18:00:00' \
    -aou degrees \
    --quiet \
    --uniplot
```

We can _zoom-out_ in time
to gain a better understanding of the solar positioning angles :

``` bash exec="true" result="ansi" source="material-block" hl_lines="3 4"
pvgis-prototype position overview \
    8.628 45.812 180 45 \
    --start-time '2010-01-17' \
    --end-time '2010-01-18' \
    -aou degrees \
    --quiet \
    --uniplot
```

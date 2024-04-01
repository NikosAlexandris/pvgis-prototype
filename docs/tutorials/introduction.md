---
icon: 
title: Photovoltaic performance
subtitle: A gentle guide into photovoltaic performance using PV(G)IS
tags:
  - Tutorial
  - Introduction
  - CLI
  - Photovoltaic Performance
  - Broadband Irradiance
---

# A gentle introduction to elements of photovoltaic performance using PVGIS

## Overview

Are you curious about photovoltaic performance ?
This is an introduction into the estimation of photovoltaic power
over a location and a moment or period in time.

We will explore solar radiation components
and photovoltaic power estimates,
by stepping through :

- the calculation of the position of the sun in the sky
- the measurement of sun-to-surface angles
- the analysis of solar irradiance components
- and the derivation of the _effective_ amount of global irradiance.

Before we walk through the tutorial,
let's get straight a/the result we are aiming at !
We want to _estimate the photovoltaic power output
for a specific location and a short period of time_.

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8 45 214 \
    --start-time '2010-01-27' \
    --end-time '2010-01-28' \
    --quiet \
    --uniplot
```

!!! tip

    Just copy-and-paste the commands and follow along.
    This is one way to practice through this tutorial!

!!! danger "Update-Me!"

    The above command will simulate the radiation components. An update is
    needed with a minimal dataset that will enable running the same commands,
    albeit, by reading the irradiance time series from SARAH3 products!

Let's break-down the result :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8 45 214 \
    --start-time '2010-01-27' \
    --end-time '2010-01-28' \
    --surface-tilt 0.0001 \
    --global-horizontal-irradiance sarah3_sis_12_076.nc \
    --direct-horizontal-irradiance sarah3_sid_12_076.nc \
    --neighbor-lookup nearest \
    -vv
```

For each hour during the period in question,
we calculated the photovoltaic power output
based on satellite-based observations of the terrestrial radiation
and a predefined efficiency and other parameters.

The `Power ⌁` column is the results of the 
`Global ∡` inclined irradiance multiplied by the overall `Efficiency %`.
In fact, the global inclined irradiance
can be broken down in its _inclined_ irradiance components
`Direct ∡`, `Diffuse ∡` and `Reflected ∡`.

!!! quote

    So,
    the aim of this tutorial
    is to explain the calculations
    that lead to the estimation of the photovoltaic power output
    for a given location and period of time.

    Alright,
    let's go through this step-by-step
    and overview some theoretical concepts too.

## Geometry

### Location & Panel Geometry

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

### Solar position

As a starting point,
the command `position`,
features a sub-command `introduction`
which explains the flow of calculations of the position of the sun
and the agle between sun-rays and the solar collector surface.

Go ahead, try it out and skim through the text :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype position introduction
```

Now that we have an overview,
let's start with the basics :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype position overview-series \
    8.628 45.812 180 45 \
    '2010-01-17 12:00' \
    -aou degrees
```

!!! info

    **The command**
    
    ```
    pvgis-prototype position overview-series \
    8.628 45.812 180 45 \
    '2010-01-17 12:00' \
    -aou degrees
    ```

    **reads** :

    - execute `pvgis-prototype` command `position` and sub-command `overview-series`
    - set
        - the longitude to `8.628` and the latitude to `45.812`
        - the surface (panel) orientation to `180` and the tilt to `45` degrees
        - the timestamp `2010-01-17 12:00`
    - output the angle quantities in `degrees`

!!! warning "Degrees or radians ?"

    By default, PVGIS returns angle figures measured in radians. This extra bit
    of `-aou` is required to get the reported numbers in degrees. Without it :

    ``` bash exec="true" result="ansi" source="material-block"
    pvgis-prototype position overview-series \
    8.628 45.812 180 45 \
    '2010-01-17 12:00'
    ```

    Let's note down the solar zenith angle (in radians) : **1.16802**

### Solar altitude and azimuth

The two solar position angles of interest are
the **solar altitude** (also referred to as solar elevation)
and the **solar azimuth**.

We can identify them individually :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype position altitude 8.628 45.812 '2010-01-17 12:00:00' -aou degrees
```

and

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype position azimuth \
    8.628 45.812 \
    '2010-01-17 12:00:00' \
    -aou degrees \
    --solar-position-model noaa
```

### Solar incidence angle

Nonetheless,
the single-most important angle in the context of photovoltaics,
is the solar incidence angle.

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype position incidence \
    8.628 45.812 \
    '2010-01-17 12:00:00' \
    -aou degrees
```

<!-- returns -->
<!--   Time                  Declination ∢   Hour Angle 🕛   Zenith ⦭   Altitude ⦩   Azimuth ⭮   Incidence ⦡ -->
<!--  ─────────────────────────────────────────────────────────────────────────────────────────────────────── -->
<!--   2010-01-17 12:00:00   -20.9036        6.29694         66.92272   23.07728     174.11928   68.9886 -->

<!-- Position  Longitude ϑ, Latitude ϕ = 8.62800, 45.81200, Orientation : 180.00000, Tilt : 45.00000 [degrees] -->
<!--      Algorithms  Timing : NOAA, Zone : UTC, Local zone : UTC, Positioning : NOAA, Incidence angle : -->
<!--                                               Sun-to-Plane -->

The solar radiation model firstly presented by Hofierka (2002),
defines as _solar incidence_
the angle between the sun-rays and the plane of the solar surface.
Or else : the angle between the position of the sun and the inclination of the
panel.

Typically, the incidence angle is defined as the one between the sun-rays and
the normal to the reference surface.
It is important to disinguish between the two, hence,
in PVGIS we call the _Sun-To-Plane_ the _complementary_ incidence angle,
where as the _Sun-to-Surface-Normal_
we call it the _typical_ incidence angle.

To get the _typical_ solar incidence angle,
one can use the optional flag `--no-complementary-incidence-angle` like so :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype position overview-series \
    8.628 45.812 180 45 \
    '2010-01-17 12:00' \
    -aou degrees \
    --no-complementary-incidence-angle
```
<!-- returns -->
<!--                                          Solar geometry overview -->

<!--   Time                  Declination ∢   Hour Angle 🕛   Zenith ⦭   Altitude ⦩   Azimuth ⭮   Incidence ⦡ -->
<!--  ─────────────────────────────────────────────────────────────────────────────────────────────────────── -->
<!--   2010-01-17 12:00:00   -20.9036        6.29694         66.92272   23.07728     174.11928   21.0114 -->

<!-- Position  Longitude ϑ, Latitude ϕ = 8.62800, 45.81200, Orientation : 180.00000, Tilt : 45.00000 [degrees] -->
<!--      Algorithms  Timing : NOAA, Zone : UTC, Local zone : UTC, Positioning : NOAA, Incidence angle : -->
<!--                                           Sun-to-Surface-Normal -->

## Solar radiation

### Simulating horizontal irradiance components

We can simulate solar irradiance components using PVGIS!

To start with,
let us check the interface of the `irradiance` commands :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance 
```

We can simulate all components of solar radiation :
*direct*, *diffuse*, *reflected* and *global*.
Let us begin, however,
with the **global** and **direct** components.
These are, after all,
the ones we will compare against the SARAH3 satellite-based observations.

#### Global horizontal irradiance

As a first step,
we can simulate the *global* ***horizontal*** irradiance
over our location of interest and moment in time :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global horizontal \
    8 45 214 \
    '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 583.6711 -->

We can see how this simulated quantity breaks down in its sub-components too :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global horizontal \
    8 45 214 \
    '2010-01-27 12:00:00' \
    -vvv
```
<!-- returns -->
  <!-- Time                  Global ⤓   Direct ⤓   Diffuse ⤓ -->
 <!-- ─────────────────────────────────────────────────────── -->
  <!-- 2010-01-27 12:00:00   476.2201   422.4538   53.76628 -->

#### Direct horizontal irradiance

We will get the same simulated *direct* ***horizontal*** estimation
by using the `direct horizontal` commands :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance direct horizontal \
    8 45 214 \
    '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 422.4538 -->

#### Diffuse horizontal irradiance

The diffuse component is the difference between *global* and *direct*.
As with the previous command examples,
we can derive the *diffuse* ***horizontal*** component via :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance diffuse horizontal \
    8 45 214 \
    '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 53.766277 -->

### Satellite observations of solar irradiance

Instead of relying on the model,
let's read-in observations of solar irradiance
from the SARAH3 data collection :

#### SARAH3 SIS

- Read the `SIS` component from SARAH3 :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype series select \
    sarah3_sis_12_076.nc 8 45 \
    '2010-01-27 12:00:00' \
    --neighbor-lookup nearest \
    --mask-and-scale \
    -v
```
<!-- returns -->
<!-- 475.00000 -->

#### SARAH3 SID

- Read the `SID` component from SARAH3 :
 
``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype series select \
    sarah3_sid_12_076.nc 8 45 \
    --neighbor-lookup nearest \
    -v \
    --mask-and-scale \
    '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 431.00000 -->

!!! tip "Optional and required parameters"

    The latter command differs from the one before in that the order of the
    optional and required input parameters is not the same. The message here is
    that : indeed, we can mix the order of optional parameters in-between as
    long as we _keep_ strictly the order of the required ones, as indicated in
    the help section of a command.

    Just run `pvgis-prototype series select` and read the help text.

Indeed,
the simulated values differ from the satellite-based observations
retrieved from the SARAH3 datasets.
Aren't they close enough ?
We need to keep in mind
that a series of assumptions and simplifications
are part of the solar radiation model.

### Direct normal irradiance

In estimating the photovoltaic power output,
the solar radiation component with the greates impact,
is the *direct* ***normal*** irradiance.

From the theory,
we know that 

$$
DNI = SID / cos(Solar Zenith Angle)
$$

!!! seealso

    Equation 3-6 from  https://www.cmsaf.eu/SharedDocs/Literatur/document/2023/saf_cm_dwd_pum_meteosat_hel_sarah_3_3_pdf.pdf?__blob=publicationFile.

1. First, let's get the _zenith__ angle in radians

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype position zenith \
    8.628 45.812 \
    '2010-01-17 12:00:00'
```

!!! danger "Bug"

    There is likely a bug in the `position zenith `command currently!

2. Next, open a Python interpreter

    ``` bash
    python 
    ```

3. Set the _direct horizontal_ irradiance reported in SARAH3
   and the _zenith_ angle calculated previously

    ```pycon exec="true" session="dni" source="above"
    >>> sid = 431.00000
    >>> solar_zenith_angle = 1.15314
    ```

4. Calculate the `DNI` using simple Pyhon

    ```pycon exec="true" session="dni" source="above"
    >>> from math import cos
    >>> print(f'DNI = {sid / cos(solar_zenith_angle)}') 
    ```
<!-- returns --> 
<!-- 959.2610440332825 -->

Let's compare with PVGIS' model :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance direct normal '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 981.2344087303509 -->

I guess we can _assume_
the model in the new software is close and not wildly out of range !
 
### Horizontal irradiance

If we simulate also the Direct Horizontal Component,
it _should_ be close to the SARAH3 observation.

Is it ? Let's find out ...

``` bash exec="true" result="ansi" source="above"
pvgis-prototype irradiance direct horizontal 8 45 214 '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 422.45524071. -->

!!! note

   Isn't this close enough to 431 ?

### Inclined irradiance

Next, the simulated *direct* ***inclined*** component : 

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance direct inclined 8 45 214 '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 420.03229235 -->

And the simulated *global* ***inclined*** component is :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 210 '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 517.2263 -->

Analytically, the above figure is broken down to its inclined components as :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined 8 45 210 '2010-01-27 12:00:00' -vvv
```

!!! attention "EXTRA" 

    If we read the _SIS_ and _SID_ SARAH3 components
    to get the Global Inclined Irradiance :

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype irradiance global inclined \
        8 45 210 \
        '2010-01-27 12:00:00' \
        --global-horizontal-irradiance sarah3_sis_12_076.nc \
        --direct-horizontal-irradiance sarah3_sid_12_076.nc \
        --neighbor-lookup nearest
    ```
    <!-- returns -->
    <!-- 898.95197 -->

    <!-- or -->

    <!-- ``` -->
      <!-- Time                  Global ∡   Direct ∡   Diffuse ∡   Reflected ∡ -->
     <!-- ───────────────────────────────────────────────────────────────────── -->
      <!-- 2010-01-27 12:00:00   898.952    816.8975   69.08706    12.96734 -->
    <!-- ``` -->

* The _diffuse inclined_ component here uses, of course,
SARAH3 SIS and SID and goes through the math to derive to `69.08706`.

### From normal to horizontal irradiance

Direct Horizontal Irradiance = Direct Normal Irradiance * sin(Solar Altitude)

!!! tip "For verification !"

    ```pycon exec="true" session="normal-to-horizontal" source="material-block"
    >>> from math import sin
    >>> dni = 1353.22228247
    >>> altitude = 0.45729
    >>> dni * sin(altitude)
    ```

## Efficiency

!!! danger "To do"

    Add content!

## Photovoltaic power

Finally, the photovoltaic power output is simulated via :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8 45 214 '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 692.26776 -->

or estimated via :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8 45 214 \
    '2010-01-27 12:00:00' \
    --global-horizontal-irradiance sarah3_sis_12_076.nc \
    --direct-horizontal-irradiance sarah3_sid_12_076.nc \
    --neighbor-lookup nearest
```
<!-- returns -->
<!-- 693.33594 -->

## Panel tilt

The default _tilt_ angle for a solar surface is `45` degrees.
In order to get the calculations done for a _horizontally flat_ panel,
we need to request this via the `--surface-tilt 0.0001` option.

Let's add it to the power commands :

- simulating the photovoltaic power output :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8 45 214 \
    '2010-01-27 12:00:00' \
    --surface-tilt 0.0001
```
<!-- returns -->
<!-- 696.8312 -->

- using SARAH3 data :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8 45 214 \
    '2010-01-27 12:00:00' \
    --surface-tilt 0.0001 \
    --global-horizontal-irradiance sarah3_sis_12_076.nc \
    --direct-horizontal-irradiance sarah3_sid_12_076.nc \
    --neighbor-lookup nearest
```
<!-- returns -->
<!-- 701.8636 -->

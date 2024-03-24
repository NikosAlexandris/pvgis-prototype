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

Are you curious about photovoltaic performance ?
This is a gentle introduction into the estimation of photovoltaic power
over a location and a moment in time.

We will explore solar radiation components
and photovoltaic power estimates,
by stepping through the calculations
of the position of the sun in the sky
and sun-to-surface angles,
analysing the solar irradiance components
and the derivation of the _effective_ amount of global irradiance.


## Location & Panel Geometry

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
 
!!! note "On the Linke Turbidity"

    By default, PVGIS does _not_ use any Linke Turbidity input
    when it gets to read solar irradiance components from external datasets,
    such as for example SARAH3 products.

    *EXPLAIN HERE MORE*

## Solar position

As a starting point for the `position` _category_ of commands,
as well as for every other _command category_,
there is an `introduction` in to the flow of calculations of the position of
the sun and the agle between sun-rays and the solar collector surface.

Go ahead and try it out :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype position introduction
```

Starting with the basics,

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype position overview-series 8.628 45.812 33 33 '2010-01-17 12:00' -aou degrees
```

!!! warning "Degrees or radians ?"

    By default, PVGIS returns angle figures measured in radians. This extra bit
    of `-aou` is required to get the reported numbers in degrees. Without it :

    ``` bash exec="true" result="ansi" source="material-block"
    pvgis-prototype position overview-series 8.628 45.812 33 33 '2010-01-17 12:00'
    ```

    Let's note down the solar zenith angle (in radians) : **1.16802**

## Simulating surface radiation

We can simulate solar irradiance components using PVGIS!

To start with,
let us check the interface of the `irradiance` commands :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance 
```

We can simulate all components of solar radiation.
Let us focus, however, at the global and direct components.
These are, after all,
the ones we will compare against the SARAH3 satellite-based observations.

As a first step,
we can simulate the global horizontal irradiance
over our location of interest and moment in time :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global horizontal 8 45 214 '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 583.6711 -->

We can see how this simulated quantity breaks down in its sub-components too :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global horizontal 8 45 214 '2010-01-27 12:00:00' -vvv
```
<!-- returns -->
  <!-- Time                  Global ⭸   Direct ⭸    Diffuse ⭸ -->
 <!-- ──────────────────────────────────────────────────────── -->
  <!-- 2010-01-27 12:00:00   583.6711   595.97107   -12.30002 -->

We will get the same simulated direct horizontal estimation
by using the `direct horizontal` commands :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance direct horizontal 8 45 214 '2010-01-27 12:00:00'
```

## External solar irradiance time series

Instead of relying on a model,
let's read-in observations of solar irradiance
from the SARAH3 data collection :

- Read the SIS component from SARAH3 :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype series select sarah3_sis_12_076.nc 8 45 --neighbor-lookup nearest -v --mask-and-scale '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 475.00000 -->

- Read the SID component from SARAH3 :
 
``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype series select sarah3_sid_12_076.nc 8 45 --neighbor-lookup nearest -v --mask-and-scale '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 431.00000 -->

Indeed,
the simulated values differ from the satellite-based observations
retrieved from the SARAH3 datasets.
We need to keep in mind, however,
a series of assumptions and simplifications are part of the solar radiation
model.

### Direct normal irradiance

In estimating the photovoltaic power output,
the solar radiation component with the greates impact,
is the direct normal irradiance.

From the theory,
we know that `DNI` = `SID / cos(Solar Zenith Angle)`

!!! seealso

    Equation 3-6 from  https://www.cmsaf.eu/SharedDocs/Literatur/document/2023/saf_cm_dwd_pum_meteosat_hel_sarah_3_3_pdf.pdf?__blob=publicationFile.

Let's get the DNI using simple Python

1. open a Python interpreter

```
python 
```

2. set the direct horizontal irradiance reported in SARAH3 

```pycon exec="true" session="dni"
>>> sid = 431.00000
>>> solar_zenith_angle = 1.10481
```

3. then do the math

```pycon exec="true" session="dni"
>>> from math import cos
>>> sid / cos(solar_zenith_angle) 
```
 
Let's compare with PVGIS' model :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance direct normal '2010-01-27 12:00:00'
```

Let's _assume_ the model in the new software is close and not wildly out of
range.
 
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

   Is this close to 431 ?

### Inclined irradiance

Next, the simulated Direct Inclined Irradiance component : 

``` bash exec="true" result="ansi" source="above"
pvgis-prototype irradiance direct inclined 8 45 214 '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 420.03229235 -->

And the simulated Global Inclined component is :

``` bash exec="true" result="ansi" source="above"
pvgis-prototype irradiance global broadband 8 45 210 '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 517.2263 -->

Analytically, the above figure is broken down to its inclined components as :

``` bash exec="true" result="ansi" source="above"
pvgis-prototype irradiance global broadband 8 45 210 '2010-01-27 12:00:00' -vvv
```

!!! attention "EXTRA" 

    If we read the SIS and SID SARAH3 components
    to get the Global Inclined Irradiance :

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype irradiance global broadband 8 45 210 '2010-01-27 12:00:00' --global-horizontal-irradiance sarah3_sis_12_076.nc --direct-horizontal-irradiance sarah3_sid_12_076.nc --neighbor-lookup nearest
    ```
    <!-- returns 511.11603 -->

    <!-- or -->

    <!-- ``` -->
    <!--  Time                  Global ∡    Direct ∡   Diffuse ∡   Reflected ∡ -->
    <!-- ──────────────────────────────────────────────────────────────────────── -->
    <!--  2010-01-27 12:00:00   511.11603   428.52805   69.61911    12.968864 -->
    <!-- ``` -->

* The diffuse inclined component here uses, of course,
SARAH3 SIS and SID and goes through the math to derive to 69.61911.


### From normal to horizontal irradiance

Direct Horizontal Irradiance = Direct Normal Irradiance * sin(Solar Altitude)

!!! note "For verification !"

    ```pycon exec="true" session="normal-to-horizontal" source="material-block"
    from math import sin
    dni = 1353.22228247
    altitude = 0.45729
    dni * math.sin(altitude)
    ```

## Efficiency


## Photovoltaic power

Finally, the PV power output is simulated via :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8 45 214 '2010-01-27 12:00:00'
```
<!-- which returns 419.39359973928754 -->

or estimated via :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8 45 214 '2010-01-27 12:00:00' --global-horizontal-irradiance tests/data/input/sarah3_sis_12_076.nc --direct-horizontal-irradiance tests/data/input/sarah3_sid_12_076.nc --neighbor-lookup nearest
```
<!-- which returns 414.64826220232 -->

## Panel tilt

The default tilt angle for a sular surface placed in the location in question,
is 45 degrees. So, in order to get the calculations done for a horizontally
flat panel, we need to request this via the `--surface-tilt 0.0001` option.

Let's add it to the power commands :

Finally, the PV power output is simulated via :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8 45 214 '2010-01-27 12:00:00' --surface-tilt 0.0001
```
<!-- - simulated : 414.2163163268762 -->

Using SARAH3 data :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8 45 214 '2010-01-27 12:00:00' --global-horizontal-irradiance tests/data/input/sarah3_sis_12_076.nc --direct-horizontal-irradiance tests/data/input/sarah3_sid_12_076.nc --neighbor-lookup nearest
```
<!-- - using SARAH3 data : 408.63105278021305. -->

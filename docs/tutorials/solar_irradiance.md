---
icon: material/sun-wireless
title: Solar Irradiance
tags:
  - Development
  - Solar Irradiance
---

## Simulating horizontal irradiance

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

### Global horizontal irradiance

As a first step,
we can simulate the *global* ***horizontal*** irradiance
over our location of interest and moment in time :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global horizontal \
    8.628 45.812 214 \
    '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 583.6711 -->

??? tip "Consult the help text!"

    It's always a good idea to consult the help for a command. While effort has
    been given to keep the same order for the input parameters,
    not all commands share the exact same required positional parameters!

    For the above command, we can get the help via 
    ``` bash exec="true" result="ansi" source="material-block"
    pvgis-prototype irradiance global horizontal
    ```


We can see how this simulated quantity breaks down in its sub-components too :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global horizontal \
    8.628 45.812 214 \
    '2010-01-27 12:00:00' \
    -vvv
```
<!-- returns -->
  <!-- Time                  Global ⤓   Direct ⤓   Diffuse ⤓ -->
 <!-- ─────────────────────────────────────────────────────── -->
  <!-- 2010-01-27 12:00:00   476.2201   422.4538   53.76628 -->

### Direct horizontal irradiance

We will get the same simulated *direct* ***horizontal*** estimation
by using the `direct horizontal` commands :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance direct horizontal \
    8.628 45.812 214 \
    '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 422.4538 -->

### Diffuse horizontal irradiance

The diffuse component is the difference between *global* and *direct*.
As with the previous command examples,
we can derive the *diffuse* ***horizontal*** component via :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance diffuse horizontal \
    8.628 45.812 \
    '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 53.766277 -->

!!! note

    The diffuse horizontal irradiance component
    does not need to know of an elevation value,
    hence compared to the command for the direct irradiance,
    the number `214` was removed in this example command.

## Satellite observations of solar irradiance

Instead of relying on the model,
let's read-in observations of solar irradiance
from the SARAH3 data collection :

### SARAH3 SIS

- Read the `SIS` component from SARAH3 :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype series select \
    sarah2_sis_over_esti_jrc.nc \
    8.628 45.812 \
    '2010-01-27 12:00:00' \
    --neighbor-lookup nearest \
    --mask-and-scale \
    -v
```
<!-- returns -->
<!-- 475.00000 -->

### SARAH3 SID

- Read the `SID` component from SARAH3 :
 
``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype series select \
    sarah2_sid_over_esti_jrc.nc \
    8.628 45.812 \
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

## Direct normal irradiance

In estimating the photovoltaic power output,
the solar radiation component with the greatest impact,
is the *direct* ***normal*** irradiance.

From the theory,
we know that 

$$
DNI = SID / cos(Solar Zenith Angle)
$$

!!! seealso

    Equation 3-6 from  https://www.cmsaf.eu/SharedDocs/Literatur/document/2023/saf_cm_dwd_pum_meteosat_hel_sarah_3_3_pdf.pdf?__blob=publicationFile.

1. First, let's get the _zenith_ angle in radians

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

We can _assume_
the model in the new software is close and not wildly out of range !
 
## Horizontal irradiance

If we simulate also the Direct Horizontal Component,
it _should_ be close to the SARAH3 observation.

Is it ? Let's find out ...

``` bash exec="true" result="ansi" source="above"
pvgis-prototype irradiance direct horizontal 8.628 45.812 214 '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 422.45524071. -->

!!! note

    Isn't this close enough to 431 ?

## Inclined irradiance

Next, the simulated *direct* ***inclined*** component : 

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance direct inclined \
    8.628 45.812 214 180 45 \
    '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 420.03229235 -->

And the simulated *global* ***inclined*** component is :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined \
    8.628 45.812 210 180 45 \
    '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 517.2263 -->

Analytically, the above figure is broken down to its inclined components as :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined \
    8.628 45.812 210 180 45 \
    '2010-01-27 12:00:00' \
    -vvv
```

!!! hint "Default orientation and tilt angles"

    The default values for the orientation and tilt angles of a solar surface
    are (currently) set to `180` and `45` degrees respectively.
    Hence, we'd get the same result if we 
    ``` bash exec="true" result="ansi" source="material-block"
    pvgis-prototype irradiance global horizontal \
        8.628 45.812 214 \
        '2010-01-27 12:00:00'
    ```

!!! attention "EXTRA" 

    If we read the _SIS_ and _SID_ SARAH3 components
    to get the Global Inclined Irradiance :

    ``` bash exec="true" result="ansi" source="material-block"
    pvgis-prototype irradiance global inclined \
        8.628 45.812 210 180 45 \
        '2010-01-27 12:00:00' \
        --global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc \
        --direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc \
        --neighbor-lookup nearest
    ```

* The _diffuse inclined_ component here uses, of course,
SARAH3 SIS and SID and goes through the math to derive to `69.08706`.

## From normal to horizontal irradiance

Direct Horizontal Irradiance = Direct Normal Irradiance * sin(Solar Altitude)

!!! tip "For verification !"

    ```pycon exec="true" session="normal-to-horizontal" source="above"
    >>> from math import sin
    >>> dni = 1353.22228247
    >>> altitude = 0.45729
    >>> dni * sin(altitude)
    ```

---
icon: 
title: A gentle introduction into photovoltaic performance using PV(G)IS
subtitle: Use PV(G)IS to estimate the photovoltaic power output over a time series based on broadband irradiance
tags:
  - Tutorial
  - Introduction
  - CLI
  - Photovoltaic Performance
  - Broadband Irradiance
---

# Introduction

Let's start step-by-step simulating the basic solar irradiance components,
up to the production of photovoltaic power output over a location and a moment
in time.

To begin with,
let's define the fundamental input parameters for our location of interest and
a moment in time :

- Location : (Lon, Lat) = (8, 45)
- Elevation : $214 m$.
- A good, clear-sky day over our location is `2010-01-27 12:00:00`.

Next, let us consider the basic _geometry_ of a solar panel :

- Orientation of the panel : South which is 180 degrees counting clock-wise
  from due North.
- Tilt of the Panel : horizontally flat panel which is $0 degrees$.

!!! note "Symbols"
 
    - The ∡ symbol means we are reporting an inclined component!
    - The calculations include the atmospheric refraction (as described in Hofierka, 2002)
    - The albedo is set to $0.2$
    - The Linke Turbidity is set to $2$
 
!!! note "On the Linke Turbidity"

   By default, PVGIS does _not_ use any Linke Turbidity input
   when it gets to read solar irradiance components from external datasets,
   such as for example SARAH3 products.

   *EXPLAIN HERE MORE*

We can simulate solar irradiance components using PVGIS!

To start with,
let us check the `irradiance` commands :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance 
```

Instead of relying on a model,
let's read-in observations of solar irradiance
from the SARAH3 data collection :

- Read the SIS component from SARAH3 :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype series select tests/data/input/sarah3_sis_12_076.nc 8 45 --neighbor-lookup nearest -v --mask-and-scale '2010-01-27 12:00:00'
```

- Read the SID component from SARAH3 :
 
``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype series select tests/data/input/sarah3_sid_12_076.nc 8 45 --neighbor-lookup nearest -v --mask-and-scale '2010-01-27 12:00:00'
```

From the theory,
we know that `DNI` = `SID / cos(Solar Zenith Angle)`

!!! seealso

    Equation 3-6 from  https://www.cmsaf.eu/SharedDocs/Literatur/document/2023/saf_cm_dwd_pum_meteosat_hel_sarah_3_3_pdf.pdf?__blob=publicationFile.

Let's get the DNI using simple Python : 

```pycon exec="true" source="console" session="dni"
sid = 431.00000
solar_zenith_angle = 1.10481
```

then

```pycon exec="true" source="console" session="dni"
sid / math.cos(solar_zenith_angle) 
```
returns
959.2610440332825
 
Let's verify the new tool works correctly :

``` bash exec="true" result="ansi" source="above"
pvgis-prototype irradiance direct normal '2010-01-27 12:00:00'
```
returns 981.23442024.

The implemented model in the new software is close.  Or not?
 
If we simulate also the Direct Horizontal Component,
it _should_ be close to the SARAH3 observation.
Is it ? Let's find out ...

``` bash exec="true" result="ansi" source="above"
pvgis-prototype irradiance direct horizontal 8 45 214 '2010-01-27 12:00:00'
```

returns 422.45524071.  This is indeed close to $431$.
 
Next, the simulated Direct Inclined Irradiance component : 

``` bash exec="true" result="ansi" source="above"
pvgis-prototype irradiance direct inclined 8 45 214 '2010-01-27 12:00:00'
```

returns $420.03229235$
 
And the simulated Global Inclined component is :


``` bash exec="true" result="ansi" source="above"
pvgis-prototype irradiance global broadband 8 45 210 '2010-01-27 12:00:00'
```

returns $517.2263$

Analytically, the above figure is broken down to its inclined components as :

```
Time                  Global ∡   Direct ∡   Diffuse ∡   Reflected ∡
────────────────────────────────────────────────────────────────────────
 2010-01-27 12:00:00   517.2869   420.0323    84.28578    12.968864
```

!!! attention "EXTRA" 

    If we read the SIS and SID SARAH3 components
    to get the Global Inclined Irradiance :

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype irradiance global broadband 8 45 210 '2010-01-27 12:00:00' --global-horizontal-irradiance sarah3_sis_12_076.nc --direct-horizontal-irradiance sarah3_sid_12_076.nc --neighbor-lookup nearest
    ```
    returns 511.11603

    or

    ```
     Time                  Global ∡    Direct ∡   Diffuse ∡   Reflected ∡
    ────────────────────────────────────────────────────────────────────────
     2010-01-27 12:00:00   511.11603   428.52805   69.61911    12.968864
     ```

* The diffuse inclined component here uses, of course,
SARAH3 SIS and SID and goes through the math to derive to $69.61911$.
 
Finally, the PV power output is simulated via :
``` bash exec="true" result="ansi" source="above"
pvgis-prototype power broadband 8 45 214 '2010-01-27 12:00:00'
```

which returns $419.39359973928754$

or estimated via :

``` bash exec="true" result="ansi" source="above"
pvgis-prototype power broadband 8 45 214 '2010-01-27 12:00:00' --global-horizontal-irradiance tests/data/input/sarah3_sis_12_076.nc --direct-horizontal-irradiance tests/data/input/sarah3_sid_12_076.nc --neighbor-lookup nearest
```

which returns $414.64826220232$

Adding the `--surface-tilt 0.0001` option
to the two power commands, we get respectively :

- simulated : $414.2163163268762$
- using SARAH3 data : $408.63105278021305.$

---
icon: material/sun-wireless
title: Solar Irradiance
tags:
  - Reference
  - Solar Irradiance
  - Components
  - Global
  - Direct
  - Diffuse
  - Sky-Diffuse
  - Sky-Reflected
  - Ground-Diffuse
  - Ground-Reflected
---

## Overview

==Solar Irradiance==
is the power per unit area (surface power density)
received from the Sun
in the form of electromagnetic radiation
in the wavelength range of the measuring instrument.
Solar irradiance is measured in watts per square metre (W/m2) in SI units.

*(source: Wikipedia)*

## Global irradiance

**Global irradiance**
represents the total solar radiation incident on a surface,
combining all three components.
It can be measured or calculated for :

- **Horizontal surfaces** (Global Horizontal Irradiance, GHI)
- **Inclined surfaces** (Global Inclined or In-Plane Irradiance, GII)

The global horizontal component serves as a fundamental input
for calculating irradiance on tilted surfaces.

PVGIS models solar irradiance incident on a tilted (or inclined) solar surface
as the sum of two fundamental components :

\[
\text{Global}\ _{inclined} = \text{Direct} + \text{Diffuse}
\]

The diffuse irradiance, however, is the sum of the sky-reflected and
ground-reflected components :

\[
\text{Global}\ _{inclined} = \text{Direct} + \text{Sky-Diffuse} + \text{Ground-Diffuse}
\]

!!! note "Reflected irradiance in PVGIS <= 5.x"

    The older generation of PVGIS version <= 5.x, names the latter component as
    Ground-Reflected.  In this documentation the terms ground-diffuse and
    ground-reflected mean the same physical quantity.
    The same _equation_ appears there in the following form :
    
    \[
    \text{Global} _(inclined) = \text{Direct} + \text{Diffuse} + \text{Reflected}
    \]

!!! info "Irradiance data in the PVGIS Web application"

    The PVGIS Web application uses the SARAHx global and direct horizontal
    irradiance products. This software however, can consume _any_ such time
    series data, as long as the data format is one that is supported by the
    Xarray library.

Each irradiance component represents a distinct physical process :

- **Direct** is the radiation arriving straight from the sun's disk.
- **Diffuse sky-reflected** is the radiation scattered by the atmosphere and clouds.
- **Diffuse ground-reflected** is the radiation reflected from the ground
  surface onto the solar collector.

PVGIS consumes time series of global and direct horizontal irradiance
to calculate the diffuse components (sky-reflected and ground-reflected).

```python exec="true" html="true"
--8<-- "docs/reference/solar_irradiance_diagram.py"
```

!!! info "Terminology & Tools"

    PVGIS CLI and output columns use consistent terminology to distinguish between irradiance components:

    | Component                | Incidence angles     | CLI Command | Subcommand/s             | Physical Meaning                      |
    |--------------------------|----------------------|-------------|--------------------------|---------------------------------------|
    | Global                   | Horizontal, Inclined | `global`    | `horizontal`, `inclined` | Total incident irradiance             |
    | Direct                   | Horizontal, Inclined | `direct`    | `horizontal`, `inclined` | Direct radiation from the sun         |
    | Diffuse Sky-reflected    | Horizontal, Inclined | `diffuse`   | `horizontal`, `inclined` | Radiation scattered by the atmosphere |
    | Diffuse Ground-reflected | Inclined             | `diffuse`   | `ground-diffuse`         | Reflected from the ground surfae      |

## Horizontal vs. Inclined Irradiance

PVGIS can output both horizontal and inclined irradiance components

- **Horizontal irradiance** is measured on a flat, horizontal surface
- **Inclined irradiance** (also called **in-plane irradiance**) is calculated for a solar surface positioned at specified orientation and tilt angles

The transformation or transposition from horizontal to inclined
involves geometric and radiometric corrections for each component
based on solar position and surface orientation.

## Horizontal vs. Inclined Irradiance

PVGIS can output both horizontal and inclined irradiance components

- **Horizontal irradiance** is measured on a flat, horizontal surface
- **Inclined irradiance** (also called **in-plane irradiance**) is calculated for a solar surface positioned at specified orientation and tilt angles

The transformation or transposition from horizontal to inclined
involves geometric and radiometric corrections for each component
based on solar position and surface orientation.

## Direct irradiance

**Direct irradiance**
is the portion of solar radiation arriving directly from the sun's disk
and without scattering.
This component is sensitive to :

- Solar position (altitude and azimuth angles)
- Atmospheric conditions (clouds, aerosols)
- Surface orientation and tilt

The direct irradiance can be expressed as :

- **Direct Normal Irradiance** (DNI) is the radiation perpendicular to the sun's rays
- **Direct Horizontal Irradiance** (DHI) is the radiation incident on a horizontal plane
- **Direct Inclined Irradiance** is the radiation incident on a tilted surface

The relationship between these quantities involves the
_solar altitude_ and _solar incidence_ angles:

\[
\text{Direct Horizontal Irradiance} = \text{Direct Normal Irradiance} \times \sin(\text{Solar Altitude})
\]

\[
\text{Direct Inclined Irradiance} = \text{Direct Horizontal Irradiance} \times \frac{\sin(\text{Solar Incidence})}{\sin(\text{Solar Altitude})}
\]

## Diffuse irradiance

### Sky-Reflected irradiance

**Diffuse irradiance** or **sky-diffuse**
represents solar radiation that has been scattered by atmospheric components
(molecules, aerosols, clouds) before reaching the surface.
The sky-reflected diffuse irradiance component :

- Does not come from the sun directly
- Arrives from all parts of the sky dome
- Is particularly significant under cloudy conditions
- Depends on atmospheric turbidity and cloud cover

For _inclined_ surfaces, the diffuse component calculation accounts for :

- The portion of the sky hemisphere visible to the surface (sky view factor)
- Whether the surface is in shade or sunlit
- Atmospheric scattering properties

!!! important "Diffuse vs. Sky-Diffuse"

    In PVGIS documentation and CLI outputs, "diffuse" and "sky-diffuse"
    are used interchangeably to refer to diffuse sky-reflected irradiance,
    distinguishing it from ground-reflected irradiance.

### Ground-reflected irradiance

**Diffuse ground-reflected irradiance** or **ground-diffuse**
is the solar radiation reflected from the ground surface
and incident on the tilted solar collector.
This component depends on :

- the **global horizontal** component : the total irradiance available for
  reflection
- **ground view fraction** : portion of ground visible from the tilted surface
  (depends on the tilt of the solar surface)
- **albedo**, the reflectivity of the ground surface

#### Calculation

The ground view fraction
is calculated as a function of the surface tilt angle
from the global horizontal component (Hofierka, 2002).
Note that the diffuse ground-reflected component is set to `0`
for a flat horizontal surface or one that is tilted close to `0` degrees.

\[
\text{Ground View Fraction} = \frac{1 - \cos(\text{Surface Tilt})}{2}
\]

The diffuse ground-reflected irradiance is then:

\[
\text{Ground-Reflected} = \text{Albedo} \times \text{GHI} \times \text{Ground View Fraction}
\]

!!! info "Key Characteristics"

    - **For horizontal surfaces** (tilt ≈ 0°): Ground-reflected component is approximately **zero** because the surface cannot "see" the ground
    - **For vertical surfaces** (tilt = 90°): Maximum ground view fraction of 0.5
    - **Increases with tilt angle**: The steeper the tilt, the more ground is visible to the surface

!!! tip "When Ground-Reflected Irradiance Matters"

    Ground-reflected irradiance becomes significant for:
    
    - Steeply tilted surfaces (tilt > 30°)
    - High-albedo environments (snow, sand, water)
    - Bifacial PV modules that can capture rear-side irradiance
    - Vertical installations (building facades)

## Effects & Corrections

### Reflectivity effect

The photovoltaic performance analysis
considers the effect of the solar surface reflectivity itself
to both direct and non-direct irradiance components
(sky-reflected and ground-reflected).

In PVGIS the reflectivity is calculated as a function of the solar incidence
angle (Martin and Ruiz, 2005).

\[
\text{Reflectivity Effect} = \text{f(Incidence)}
\]

Note that there is a difference between the mathematical equations applied 
to the direct and non-direct components.

The photovoltaic performance analysis considers **reflectivity losses** due to:

- Solar incidence angle (larger angles → more reflection)
- Surface properties (glass type, anti-reflection coatings)

Reflectivity is calculated as a function of the solar incidence angle (Martin and Ruiz, 2005):

\[
\text{Reflectivity Effect} = f(\text{Solar Incidence Angle})
\]

Note that different mathematical equations apply to:

- **Direct irradiance** (depends on exact incidence angle)
- **Diffuse components** (sky-diffuse and ground-reflected, averaged over hemisphere)

### Spectral Effect

The **spectral effect** accounts for differences between:

- Natural sunlight spectrum (varies with atmospheric conditions, solar position)
- Standard Test Conditions (STC) reference spectrum (AM1.5)

\[
\text{Spectral Effect} = \frac{\text{STC Spectrum}}{\text{Actual Sunlight Spectrum}}
\]

This correction is particularly important for different PV technologies that have varying spectral responses.

## References

- Hofierka, J. (2002). Solar radiation model. In *Distributed GRASS Modules for Solar Irradiance Modelling*.
- Martin, N., & Ruiz, J. M. (2005). Annual angular reflection losses in PV modules. *Progress in Photovoltaics: Research and Applications*, 13(1), 75-84.
- SARAH-2/3 Climate Data Records: Surface Solar Radiation. CM SAF, EUMETSAT.
```

<!-- ## See Also -->

<!-- - [Solar Position](solarposition.md) - Angular calculations for sun-surface geometry -->
<!-- - [Photovoltaic Performance](photovoltaicperformance.md) - How irradiance components affect PV output -->
<!-- - [Tutorials: Solar Irradiance](../tutorials/solarirradiance.md) - Hands-on examples with CLI commands -->

---
icon: material/sun-wireless
title: Solar Irradiance
tags:
  - Reference
  - Solar Irradiance
  - Introduction
---

==Solar Irradiance==
is the power per unit area (surface power density)
received from the Sun
in the form of electromagnetic radiation
in the wavelength range of the measuring instrument.
Solar irradiance is measured in watts per square metre (W/m2) in SI units.
(source: Wikipedia)


PVGIS calculates the global in-plane (or inclined) irradiance as follows:

    Global (inclined) = Direct + Diffuse + Reflected.

The default source for the global and direct horizontal irradiance components
is SARAH2/2 products.
The diffuse components (sky-reflected and ground-reflected)
are calculated based on former inputs.

### Ground-reflected irradiance

The ground-reflected irradiance incident on an inclined surface depends on :

- the global horizontal component
- ground view fraction (depends on the tilt of the solar surface)
- albedo value which is pre-set to `xx`

The ground view fraction
is calculated from the global horizontal component (Hofierka, 2002).
Note that the ground-reflected component is set to `0`
for a flat horizontal surface or one that is tilted close to 0 degrees.

### Reflectivity effect

The photovoltaic performance analysis
considers the effect of reflectivity
to both direct and non-direct irradiance components
(sky-reflected and ground-reflected).
The reflectivity is calculated as a function of the solar incidence angle
(Martin and Ruiz, 2005).
Note that there is a difference between the mathematical equations applied 
to the direct and non-direct components.


!!! warning "DRAFT Text"

    ### Normal Irradiance

    ### Horizontal irradiance

        Calculation of the global horizontal irradiance which is the sum of three
        components : the direct horizontal irradiance, the sky-reflected irradiance
        and the ground-reflected irradiance. Hereafter, irradiance (i.e. _Horizontal
        irradiance_) refers to the _global_ irradiance.

        - Horizontal = Normal * Altitude

        > Note : In the context of PVGIS and throughout the source code, the _Inclined_ irradiance is an homonym for the _In-Plane_ irradiance.

    ### In-Plane irradiance

        In-plane or Inclined irradiance

    ### Effects

    #### Reflectivity effect

        The reflectivity effect is calculated as a function of the incidence angle : Reflectivity Effect = f(Incidence).

    #### Spectral effect

            Spectral Effect Ratio = STC-Light ~ Sunlight

    #### System loss

## Processing solar irradiance time series

```python exec="true" html="true"
--8<-- "docs/reference/solar_irradiance_diagram.py"
```

---
icon: material/solar-power-variant
title: Photovoltaic Performance
tags:
  - pvgisprototype
  - Photovoltaic
  - Performance
  - Analysis
---

!!! danger "DRAFT"

    A key metric for evaluating the overall performance of a photovoltaic (PV)
    system is the cumulative [yellow]Energy[/yellow] produced over a time period
    (e.g., daily, monthly, or annual). In other words, energy production is an
    arbitrary aggregate of the instantaneous power estimations over a time series.
    In turn, the instantaneous (effective irradiance, and thereby) power values
    reflect the [italic]current[/italic] output of the photovoltaic (PV) system
    at each moment in time.
    How does PVGIS calculcate photovoltaic power output ?

    1. We calculcate the position of the sun in the sky relative to the
    positioning of a solar surface. Essentially this boils down to one
    trigonometric paramter : the solar incidence angle. This angle depends on the
    solar altitude and solar azimuth angles on any given moment in time combined
    with the location, the orientation and the tilt of the solar surface itself.

    2. We ..

    Analytically, we can break down the algorith as follows:
    Let us go through the calculation step-by-step.

    Hence, .. :

    1. Define an arbitrary period of time

    2. Calculate the solar altitude angle series

    3. Calculate the solar azimuth angle series

    4. Derive masks of the position of the sun :

      i. above the horizon and not in shade
      ii. very low sun angles
      iii. below the horizon

    5. Calculate the direct horizontal irradiance component for ..

    6. Calculate the diffuse and reflected irradiance components for the sun above
    the horizon

    7. Sum the individual irradiance components to derive the global inclined
    irradiance

    8. Read time series of the ambient temperature, the wind speed and the spectral factor

    9. Derive the conversion efficiency coefficients

    10. Estimate the photovoltaic power as the product of the global irradiance and
    the efficiency coefficients.


## Power-rating model

The power-rating model used in PVGIS {cite}`Huld2011`
is particularly effective for crystalline silicon photovoltaic (PV) modules
and incorporates various coefficients determined through both indoor and
outdoor performance data established in [ESTI](https://joint-research-centre.ec.europa.eu/european-solar-test-installation_en).

```python exec="true" html="true"
--8<-- "docs/reference/photovoltaic_performance_diagram.py"
```

### Icons

- Solar Power by Blangcon from <a href="https://thenounproject.com/browse/icons/term/solar-power/" target="_blank" title="Solar Power Icons">Noun Project</a> (CC BY 3.0)

- solar panel by Arkinasi from <a href="https://thenounproject.com/browse/icons/term/solar-panel/" target="_blank" title="solar panel Icons">Noun Project</a> (CC BY 3.0)

- sun by Jolan Soens from <a href="https://thenounproject.com/browse/icons/term/sun/" target="_blank" title="sun Icons">Noun Project</a> (CC BY 3.0)

- fluorescent by H Alberto Gongora from <a href="https://thenounproject.com/browse/icons/term/fluorescent/" target="_blank" title="fluorescent Icons">Noun Project</a> (CC BY 3.0)

- solar energy by Cocoa Bella from <a href="https://thenounproject.com/browse/icons/term/solar-energy/" target="_blank" title="solar energy Icons">Noun Project</a> (CC BY 3.0)

- reflection by Iconbunny from <a href="https://thenounproject.com/browse/icons/term/reflection/" target="_blank" title="reflection Icons">Noun Project</a> (CC BY 3.0)

- Windsock by Dani Pomal from <a href="https://thenounproject.com/browse/icons/term/windsock/" target="_blank" title="Windsock Icons">Noun Project</a> (CC BY 3.0) 

- electromagnetic by Amethyst Studio from <a href="https://thenounproject.com/browse/icons/term/electromagnetic/" target="_blank" title="electromagnetic Icons">Noun Project</a> (CC BY 3.0)

- Rainbow by VectorRecipe7 from <a href="https://thenounproject.com/browse/icons/term/rainbow/" target="_blank" title="Rainbow Icons">Noun Project</a> (CC BY 3.0)

- millimeter wave by shashank singh from <a href="https://thenounproject.com/browse/icons/term/millimeter-wave/" target="_blank" title="millimeter wave Icons">Noun Project</a> (CC BY 3.0)

- Scattered Material by Stephen Plaster from <a href="https://thenounproject.com/browse/icons/term/scattered-material/" target="_blank" title="Scattered Material Icons">Noun Project</a> (CC BY 3.0)

- User by Aswell Studio from <a href="https://thenounproject.com/browse/icons/term/user/" target="_blank" title="User Icons">Noun Project</a> (CC BY 3.0)

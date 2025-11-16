---
icon: material/solar-power-variant-outline
tags:
  - How-To
  - CLI
  - Solar Surface
  - Solar Surface Position
  - Optimal Solar Surface Position
hide:
  - toc
---

What is the _best_ placement of a solar surface for a day ?

``` bash exec="true" result="ansi" source="above"
pvgis-prototype surface optimise \
8.628 45.812 214 \
--start-time '2010-01-01'  \
--end-time '2010-01-02'
```

We'd also want the output in degrees along with a fingerprint.

``` bash exec="true" result="ansi" source="above" hl_lines="5 6"
pvgis-prototype surface optimise \
8.628 45.812 214 \
--start-time '2010-01-01' \
--end-time '2010-01-02' \
-aou degrees \
--fp
```

Of course,
we can select the photovoltaic technology
which essentially tweaks some efficiency coefficients
as part of the estimation of the photovoltaic power output.

``` bash exec="true" result="ansi" source="above" hl_lines="5"
pvgis-prototype surface optimise \
8.628 45.812 214 \
--start-time '2010-01-01' \
--end-time '2010-01-02' \
--photovoltaic-module 'CIS:Integrated' \
-aou degrees \
--fp
```

!!! note "The fingerprint"

    Observe how the different set of input parameters
    generate in the end a unique fingerprint.
    This helps to verify that operations are unique
    -- even if (composing different input parameters)
    we obtain the same result.

Say the options of placing a photovoltaic panel
(i.e. a _solar surface_ in PVGIS' dialect)
are somewhat limited.

We can limit the range of positioning angles
for the solar surface itself !


``` bash exec="true" result="ansi" source="above" hl_lines="6 7 8 9"
pvgis-prototype surface optimise \
8.628 45.812 214 \
--start-time '2010-01-01' \
--end-time '2010-01-02' \
--photovoltaic-module 'CIS:Integrated' \
--min-surface-orientation 166 \
--max-surface-orientation 199 \
--min-surface-tilt 11 \
--max-surface-tilt 88 \
-aou degrees \
--fp
```

We can also dive deeper in mathematical options,
such as the sampling method or sample size
with which the optimisation algorithm operates

``` bash exec="true" result="ansi" source="above" hl_lines="10"
pvgis-prototype surface optimise \
8.628 45.812 214 \
--start-time '2010-01-01' \
--end-time '2010-01-02' \
--photovoltaic-module 'CIS:Integrated' \
--min-surface-orientation 155 \
--max-surface-orientation 188 \
--min-surface-tilt 12 \
--max-surface-tilt 88 \
--shgo-sampling-method halton \
-aou degrees \
--fp
```

See the difference ?

``` bash exec="true" result="ansi" source="above" hl_lines="10"
pvgis-prototype surface optimise \
3 33 2000 \
--start-time '2010-01-01' \
--end-time '2010-01-02' \
--fp \
-v \
-aou degrees \
--min-surface-orientation 44 \
-v
```

---
icon: material/decimal-comma-decrease
title: Precision
tags:
  - CLI
  - Precision
---

## Rounding decimals

For detailed outputs obtained via the verbosity flag/s,
we can ask to round the output values down to a specific number of decimals

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 180 45 \
    '2010-01-27 12:00:00' \
    -v \
    --rounding-places 3
```

or even

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 180 45 \
    '2010-01-27 12:00:00' \
    -vvv \
    --rounding-places 1
```

## Higher precision

Do you really need higher precision?
Head over to the [NumPy](../cli/numpy.md) section.

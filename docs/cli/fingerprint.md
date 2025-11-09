---
icon: material/fingerprint
description: Unique output fingerprint
title: Fingerprint
subtitle: Fingerprint calculation output
tags:
  - How-To
  - CLI
  - Fingerprint
---

For each and every command
we can request for a **fingerprint** of the output :

``` bash exec="true" result="ansi" source="material-block" hl_lines="6"
pvgis-prototype power broadband \
    8 45 214 167 \
    --start-time '2000-01-01' \
    --end-time '2020-12-31' \
    --quiet \
    --fingerprint
```

Every bit of _difference_ in the input parameters,
will derive a _unique_ fingerprint.
Let's modify slightly the above command
(set the surface orientation to `168`)
and re-run it to verify the new fingerprint :

``` bash exec="true" result="ansi" source="material-block" hl_lines="2"
pvgis-prototype power broadband \
    8 45 214 168 \
    --start-time '2000-01-01' \
    --end-time '2020-12-31' \
    --quiet \
    --fingerprint
```

One more example :
let's read data from external solar irradiance time series
and ask for a `--uniplot` along with the `--fingerprint` :

``` bash exec="true" result="ansi" source="material-block" hl_lines="5 6 9 10"
pvgis-prototype power broadband \
    8.628 45.812 214 \
    --start-time '2010-01-27' \
    --end-time '2010-01-28' \
    --global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc \
    --direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc \
    --neighbor-lookup nearest \
    --quiet \
    --uniplot \
    --fingerprint
```

---
icon: material/fingerprint
description: Unique output fingerprint
title: Fingerprint
subtitle: Fingerprinting calculated outputs
tags:
  - How-To
  - CLI
  - Fingerprint
---

### Unique outputs

We can _time_ the duration of a command that processes a long time series using
the terminal's built-in function `time` :

``` bash exec="true" result="ansi" source="material-block"
time pvgis-prototype power broadband 8 45 214 167 --start-time '2000-01-01' --end-time '2020-12-31' --quiet --fingerprint
```

``` bash exec="true" result="ansi" source="material-block"
time pvgis-prototype power broadband 8 45 214 167 --start-time '2000-01-01' --end-time '2020-12-31' --quiet --fingerprint --uniplot
```

``` bash exec="true" result="ansi" source="material-block"
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

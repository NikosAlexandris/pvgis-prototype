---
icon: simple/liberadotchat
title: Diffuse irradiance
subtitle: Diffuse sky- & ground-reflected irradiance
tags:
  - How-To
  - CLI
  - Diffuse
  - Diffuse Horizontal
  - Diffuse Inclined
  - Sky-Reflected
  - Ground-Reflected
hide:
  - toc
---

In PVGIS,
the diffuse irradiance
is the sum of the sky-reflected and ground-reflected components.
The **sky-reflected** component
is the radiation scattered by the atmosphere and clouds.
and the **ground-reflected**
is the radiation reflected from the ground surface onto the solar collector.

To begin with, let's see the relevant sub/commands by running

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance diffuse
```

The following sections exempliy how-to work with these commands.

## Diffuse inclined

Let's calculate the direct inclined irradiance over the location at 
(longitude, latitude, elevation) = $$8.627626 45.812233 200$$


``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance diffuse inclined \
    8.628 45.812 214 \
    --start-time '2010-01-27' \
    --end-time '2010-01-28'
```

or indeed a bit more detailed

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance diffuse inclined \
    8.628 45.812 214 \
    --start-time '2010-01-27' \
    --end-time '2010-01-28' \
    -v
```

We can do this for 2 years, for example, and add a quick plot along with a
fingerprint which can be handy to verify the output in case we want to
reproduce it

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance diffuse inclined \
    8.628 45.812 214 \
    --start-time '2010-01-01' \
    --end-time '2011-12-31' \
    --fingerprint \
    --uniplot \
    --quiet
```

## Diffuse horizontal

> Does not require elevation !

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance diffuse horizontal \
    8.628 45.812 \
    --start-time '2013-06-01' \
    --end-time '2013-06-02' \
    -vvvvv
```

## :material-triangle-wave: Ground-Reflected

!!! danger "Incomplete"

    This section is yet to be completed !

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance diffuse ground-reflected \
    8.628 45.812 214 \
    --start-time '2010-01-27' \
    --end-time '2010-01-28' \
    -v
```

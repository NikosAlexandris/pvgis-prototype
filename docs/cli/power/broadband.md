---
icon: simple/spectrum
title: Photovoltaic performance based on broadband irradiance
subtitle: Estimate photovoltaic performance over a time series based on broadband irradiance
tags:
  - How-To
  - CLI
  - Photovoltaic Performance
  - Broadband Irradiance
---

# Broadband irradiance

PVGIS can estimate the photovoltaic power over a time series or an arbitrarily aggregated energy production of a PV system based on broadband irradiance, ambient temperature and wind speed.

## Example

<div class="termy">

```console
$ pvgis-prototype power broadband 8.627626 45.81223 200 --start-time '2000-01-01' --end-time '2000-01-02'
---> 100%
nan,nan,nan,nan,nan,nan,nan,nan,125.35688423614582,260.5353314553751,357.0126776097902,397.73380205958784,396.8388479053645,353.32665433982226,254.19124368612873,118.2694763348484,nan,nan,nan,nan,nan,nan,nan,nan,nan
```

</div>

### Verbosity levels

The commands returned the PV power output
at hourly frequency for the requested period of time.
Eventually we want to know more about the calculated figures. We can ask for
more details via the _verbosity_ flag `-v` :

!!! note "A fake interactive example"

    The following example is a hardcoded one for the sake of simulating the
    interactive nature of the command line interface. Most of the commands,
    however, throughout the documentation, are real commands executed at the
    documentation's built time.

<div class="termy">

```console
$ pvgis-prototype power broadband 8.627626 45.81223 200 --start-time '2000-01-01' --end-time '2000-01-02' -v
---> 100%
                     Power series ㎾h

  Longitude   Latitude   Time                  ⌁ Power
 ────────────────────────────────────────────────────────
  0.15058     0.79957    2000-01-01 00:00:00   nan
  0.15058     0.79957    2000-01-01 01:00:00   nan
  0.15058     0.79957    2000-01-01 02:00:00   nan
  0.15058     0.79957    2000-01-01 03:00:00   nan
  0.15058     0.79957    2000-01-01 04:00:00   nan
  0.15058     0.79957    2000-01-01 05:00:00   nan
  0.15058     0.79957    2000-01-01 06:00:00   nan
  0.15058     0.79957    2000-01-01 07:00:00   nan
  0.15058     0.79957    2000-01-01 08:00:00   125.35688
  0.15058     0.79957    2000-01-01 09:00:00   260.53533
  0.15058     0.79957    2000-01-01 10:00:00   357.01268
  0.15058     0.79957    2000-01-01 11:00:00   397.73380
  0.15058     0.79957    2000-01-01 12:00:00   396.83885
  0.15058     0.79957    2000-01-01 13:00:00   353.32665
  0.15058     0.79957    2000-01-01 14:00:00   254.19124
  0.15058     0.79957    2000-01-01 15:00:00   118.26948
  0.15058     0.79957    2000-01-01 16:00:00   nan
  0.15058     0.79957    2000-01-01 17:00:00   nan
  0.15058     0.79957    2000-01-01 18:00:00   nan
  0.15058     0.79957    2000-01-01 19:00:00   nan
  0.15058     0.79957    2000-01-01 20:00:00   nan
  0.15058     0.79957    2000-01-01 21:00:00   nan
  0.15058     0.79957    2000-01-01 22:00:00   nan
  0.15058     0.79957    2000-01-01 23:00:00   nan
  0.15058     0.79957    2000-01-02 00:00:00   nan
```

</div>

and even more by adding to `v`s, i.e. `--vv` as in

``` bash exec="true" result="ansi" source="above"
pvgis-prototype power broadband 8.627626 45.81223 200 --start-time '2000-01-01' --end-time '2000-01-02' -vv
```

and even more via `-vvv` or `-vvvv` and `-vvvvv`.

!!! warning "On the number of verbosity levels"

    The number of available detail levels is not the same for all commands in
    PVGIS. At the moment, it takes for some exploration to discover what useful
    information each commad can reveal!

### Statistics

We can also ask from PVGIS to generate a statistical overview.
Following, we repeat the same calculations however extented over a year's
period, like so :


``` bash exec="true" result="ansi" source="above"
pvgis-prototype power broadband 8.627626 45.81223 200 --start-time '2000-01-01' --end-time '2000-01-02' --statistics -v
```

#### Group by

We can do better and ask for a 2-hours aggregation :

``` bash exec="true" result="ansi" source="above"
pvgis-prototype power broadband 8.627626 45.81223 200 --start-time '2000-01-01' --end-time '2000-01-02' --statistics -v --groupby 2h
```

### Plots in the command line

``` bash exec="true" result="ansi" source="above"
pvgis-prototype power broadband 8.627626 45.81223 200 --start-time '2005-06-01' --end-time '2005-06-02' --surface-tilt 45 --surface-orientation 180 -v -aou degrees --uniplot -vv
```

### Reading from external solar irradiance time series

!!! warning "Hardcoded example!"

    The following example is a fake one. Due to large file size of the external
    time series used in the command and the need to avoid committing such large
    data in the Git repository, we showcase the use of external time series
    without having the command really executed at the documentation's buit
    time. All this is subject to Updates!

<div class="termy">

```console
pvgis-prototype power broadband 8.627626 45.81223 200 \
    --start-time '2005-06-01'\
    --end-time '2005-06-02'\
    --surface-tilt 45\
    --surface-orientation 180\
    -aou degrees\
    --global-horizontal-irradiance sarah2_sis_12_076_rescaled.nc\
    --direct-horizontal-irradiance sarah2_sid_12_076_rescaled.nc\
    --neighbor-lookup nearest\
    -vv\
    --uniplot\
    --terminal-width-fraction 0.46


  Time                  ⌁ Power      Efficiency %   Algorithm   Global ∡     Direct ∡     Diffuse ∡   Reflected ∡
 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  2005-06-01 00:00:00   0.00000      0.86000        King        0.00000      0.00000      0.00000     0.00000
  2005-06-01 01:00:00   0.00000      0.86000        King        0.00000      0.00000      0.00000     0.00000
  2005-06-01 02:00:00   0.00000      0.86000        King        0.00000      0.00000      0.00000     0.00000
  2005-06-01 03:00:00   0.00000      0.86000        King        0.00000      0.00000      0.00000     0.00000
  2005-06-01 04:00:00   0.15096      0.18054        King        0.83617      0.00000      0.00000     0.83617
  2005-06-01 05:00:00   199.19998    0.82167        King        242.43294    0.00000      237.64904   4.78390
  2005-06-01 06:00:00   163.52879    0.81886        King        199.70236    2.41870      187.30454   9.97912
  2005-06-01 07:00:00   465.06577    0.80553        King        577.34087    101.94155    460.11382   15.28550
  2005-06-01 08:00:00   437.83618    0.80872        King        541.39076    40.95168     480.33550   20.10359
  2005-06-01 09:00:00   614.95357    0.78442        King        783.95711    134.69405    625.25310   24.00996
  2005-06-01 10:00:00   614.47319    0.78450        King        783.26861    95.48047     661.07781   26.71033
  2005-06-01 11:00:00   1044.44816   0.69376        King        1505.48631   1296.45330   181.01681   28.01621
  2005-06-01 12:00:00   1043.79379   0.69394        King        1504.15051   1278.35900   197.94968   27.84182
  2005-06-01 13:00:00   987.97647    0.70875        King        1393.96286   997.97909    369.78506   26.19872
  2005-06-01 14:00:00   897.77596    0.73039        King        1229.16517   648.36850    557.59916   23.19752
  2005-06-01 15:00:00   867.21265    0.73718        King        1176.39852   576.35839    580.99131   19.04882
  2005-06-01 16:00:00   799.43839    0.75134        King        1064.02172   487.80067    562.14360   14.07745
  2005-06-01 17:00:00   555.49017    0.79345        King        700.09040    130.88107    560.46817   8.74116
  2005-06-01 18:00:00   280.65333    0.82153        King        341.62459    0.00000      337.92920   3.69540
  2005-06-01 19:00:00   0.00330      0.00878        King        0.37544      0.00000      0.00000     0.37544
  2005-06-01 20:00:00   0.00000      0.86000        King        0.00000      0.00000      0.00000     0.00000
  2005-06-01 21:00:00   0.00000      0.86000        King        0.00000      0.00000      0.00000     0.00000
  2005-06-01 22:00:00   0.00000      0.86000        King        0.00000      0.00000      0.00000     0.00000
  2005-06-01 23:00:00   0.00000      0.86000        King        0.00000      0.00000      0.00000     0.00000
  2005-06-02 00:00:00   0.00000      0.86000        King        0.00000      0.00000      0.00000     0.00000
                                 (ϑ Longitude, ϕ Latitude) = (8.627626, 45.81223),
      ⌁ : Power, ⭍ : Effective component, 🗤 : Diffuse, ☈ : Reflected, ∡ : On inclined plane, ↻ : Orientation
                                     Photovoltaic power output
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                            ▛▀▀▀▀▀▚▄▄                                            │ 1,000 ㎾h
│                                           ▞        ▝▀▄▖                                         │
│                                          ▗▘           ▝▀▚▄▄▄                                    │
│                                          ▞                  ▀▀▄▄                                │
│                                         ▗▘                     ▝▖                               │
│                                         ▌                       ▝▖                              │
│                                    ▄▄▄▖▐                         ▝▖                             │
│                                   ▞▘  ▝▘                          ▝▄                            │
│                                 ▗▞                                 ▝▖                           │ 500 ㎾h
│                            ▛▄▄▄▄▘                                   ▝▖                          │
│                           ▞                                          ▝▖                         │
│                          ▞                                            ▝▖                        │
│                         ▗▘                                             ▐                        │
│                    ▄▄  ▗▘                                               ▚                       │
│                  ▗▞  ▀▀▘                                                 ▚                      │
│                 ▗▘                                                        ▚                     │
│▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▘▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▚▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄│ 0 ㎾h
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                 5                  10                  15                  20                  25
                                               ██ P

```

</div>

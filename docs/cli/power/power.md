---
title: Estimate the photovoltaic performance
subtitle: Estimate photovoltaic performance over a time series
icon: material/solar-power 
tags:
  - How-To
  - CLI
---

# Photovolatic Power

## Broadband irradiance

PVGIS can estimate the photovoltaic power over a time series or an arbitrarily aggregated energy production of a PV system based on broadband irradiance, ambient temperature and wind speed.

### Example

<div class="termy">

```console
$ pvgis-prototype power broadband 8.627626 45.81223 200 --start-time '2000-01-01' --end-time '2000-01-02'
---> 100%
nan,nan,nan,nan,nan,nan,nan,nan,125.35688423614582,260.5353314553751,357.0126776097902,397.73380205958784,396.8388479053645,353.32665433982226,254.19124368612873,118.2694763348484,nan,nan,nan,nan,nan,nan,nan,nan,nan
```

</div>

#### Verbosity levels

The commands returned the PV power output
at hourly frequency for the requested period of time.
Eventually we want to know more about the calculated figures. We can ask for
more details via the _verbosity_ flag `-v` :

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

<div class="termy">

```console
❯ pvgis-prototype power broadband 8.627626 45.81223 200 --start-time '2000-01-01' --end-time '2000-01-02' -vv

                                                Power & in-plane components series ㎾h

  Longitude   Latitude   Time                  ⌁ Power     Efficiency %   Algorithm   Global ∡    Direct ∡    Diffuse ∡   Reflected ∡
 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  0.15058     0.79957    2000-01-01 00:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
  0.15058     0.79957    2000-01-01 01:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
  0.15058     0.79957    2000-01-01 02:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
  0.15058     0.79957    2000-01-01 03:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
  0.15058     0.79957    2000-01-01 04:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
  0.15058     0.79957    2000-01-01 05:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
  0.15058     0.79957    2000-01-01 06:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
  0.15058     0.79957    2000-01-01 07:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
  0.15058     0.79957    2000-01-01 08:00:00   125.35688   0.81229        King        154.32494   67.15238    62.08863    25.08393
  0.15058     0.79957    2000-01-01 09:00:00   260.53533   0.82217        King        316.88928   178.75298   78.68449    59.45182
  0.15058     0.79957    2000-01-01 10:00:00   357.01268   0.81672        King        437.13092   262.33346   88.44851    86.34895
  0.15058     0.79957    2000-01-01 11:00:00   397.73380   0.81299        King        489.22092   295.87449   92.78974    100.55669
  0.15058     0.79957    2000-01-01 12:00:00   396.83885   0.81308        King        488.06677   295.23171   92.67527    100.15980
  0.15058     0.79957    2000-01-01 13:00:00   353.32665   0.81702        King        432.45751   259.14750   88.07999    85.23002
  0.15058     0.79957    2000-01-01 14:00:00   254.19124   0.82230        King        309.12309   173.34652   77.99230    57.78426
  0.15058     0.79957    2000-01-01 15:00:00   118.26948   0.81047        King        145.92761   61.53412    61.06643    23.32707
  0.15058     0.79957    2000-01-01 16:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
  0.15058     0.79957    2000-01-01 17:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
  0.15058     0.79957    2000-01-01 18:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
  0.15058     0.79957    2000-01-01 19:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
  0.15058     0.79957    2000-01-01 20:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
  0.15058     0.79957    2000-01-01 21:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
  0.15058     0.79957    2000-01-01 22:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
  0.15058     0.79957    2000-01-01 23:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
  0.15058     0.79957    2000-01-02 00:00:00   nan         nan            King        0.00000     0.00000     0.00000     0.00000
```

</div>

and even more via `-vvv` or `-vvvv` and `-vvvvv`.

!!! warning "On the number of verbosity levels"

    The number of available detail levels is not the same for all commands in
    PVGIS. At the moment, it takes for some exploration to discover what useful
    information each commad can reveal!

#### Statistics

We can also ask from PVGIS to generate a statistical overview.
Following, we repeat the same calculations however extented over a year's
period, like so :

<div class="termy">

``` console
$ pvgis-prototype power broadband 8.627626 45.81223 200 --start-time '2000-01-01' --end-time '2001-01-02' --statistics -v


              Photovoltaic power output

           Statistic   Value
 ────────────────────────────────────────────────────
               Start   2000-01-01T00:00:00.000000000
                 End   2001-01-02T00:00:00.000000000
               Count   4469

                 Min   -24753140.95838059
     25th Percentile   nan
                Mean   -5085.70760190153
              Median   451.78286769228265
                Mode   nan
                 Max   909.6092140349535
                 Sum   -22728027.27289794
            Variance   137078457294.95874
  Standard deviation   370241.07996676804

         Time of Min   2000-01-12T16:00:00.000000000
        Index of Min   280
         Time of Max   2000-06-20T11:00:00.000000000
        Index of Max   4115

                     Caption text
```

</div>

We can do better and ask for a monthly aggregation :

<div class="termy">

``` console
...
```

</div>

## Spectrally resolved irradiance

PVGIS can estimate the photovoltaic power over a time series
or an arbitrarily aggregated energy production of a PV system
based on spectrally resolved irradiance,
ambient temperature and wind speed.

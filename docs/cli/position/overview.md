---
icon: material/sun-angle
tags:
  - How-To
  - CLI
  - Solar Position
  - Solar Incidence Angle
hide:
  - toc
---

## Time series

To get a time series of solar position parameters over a location,
you can use the `pvgis-prototype position overview` command.

``` bash exec="true" result="ansi" source="above"
pvgis-prototype position overview \
8.627626 45.812233 \
--start-time '2020-01-01' \
--end-time '2020-01-02' \
-r2 \
-aou degrees
```

!!! example "What does this command do ?"

    **The command**
    
    ``` bash 
    pvgis-prototype position overview \
    8.627626 45.812233 \
    --start-time '2020-01-01' \
    --end-time '2020-01-02' \
    -r2 \
    -aou degrees
    ```

    **does** :

    - execute `pvgis-prototype` command `position` and sub-command `overview`
    - set
        - the longitude to `8.627626` and the latitude to `45.812233`
        - the surface (panel) orientation is set by default to `180` and the tilt to `45` degrees
        - the start time of the period for which to run calculations is `2020-01-01 00:00`
        - the end time of the period in question is `2020-01-02 00:00`

    - output
        - the numerical output values will be rounded to the 2nd digit
        - the angle quantities in `degrees`

### CSV

We can export the results in the widely known and machine readable CSV format

``` bash exec="true" result="ansi" source="above" hl_lines="7"
pvgis-prototype position overview \
8.627626 45.812233 \
--start-time '2020-01-01' \
--end-time '2020-01-02' \
-r2 \
-aou degrees \
--csv solar_incidence_angle_sample.csv
```

Let's verify it worked well

``` bash exec="true" result="ansi" source="above"
file solar_incidence_angle_sample.csv
```

??? note "solar_incidence_angle_sample.csv"

    {{ read_csv('docs/data/solar_incidence_angle_sample.csv') }}

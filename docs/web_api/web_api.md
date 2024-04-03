---
icon: simple/fastapi
title: Run the Web API server
tags:
  - How-To
  - Web API
  - Server
  - uvicorn
---

# Run the PVGIS Web API server

If you wish to test/run the Web API,
you can run it locally as follows :

<div class="termy">

``` console
$ cd pvgisprototype
$ uvicorn pvgisprototype.webapi:app --reload
INFO:     Will watch for changes in these directories: ['pvgis-prototype']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [134186] using StatReload
INFO:     Started server process [134188]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

By default, the server will run on http://127.0.0.1:8000.
We can run on another address, like so :

<div class="termy">

``` console
$ cd pvgisprototype
$ uvicorn pvgisprototype.webapi:app --reload --host 127.0.0.2
INFO:     Will watch for changes in these directories: ['pvgis-prototype']
INFO:     Uvicorn running on http://127.0.0.2:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [134186] using StatReload
INFO:     Started server process [134188]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

Click on the URL and you should be landing in a page like

<!-- <figure markdown> -->
  ![PVGIS Web API](../images/pvgis-prototype_web_api_uvicorn_2024-01-26.png)
  <!-- <figcaption>Image caption</figcaption> -->
<!-- </figure> -->

# Request examples

Then, demonstration of an endpoint

## Solar `time` again

- [`http://localhost:8000/calculate_solar_time_skyfield/?longitude=-70&latitude=40&timestamp=2023-06-26T12:00:00&timezone=America/New_York`](http://localhost:8000/calculate_solar_time_skyfield/?longitude=-70&latitude=40&timestamp=2023-06-26T12:00:00&timezone=America/New_York)

    - functin   : `calculate_solar_time_skyfield`
    - longitude : -70
    - latitude  : 40
    - timestamp : 2023-06-26T12:00:00
    - timezone  : 'America/New_York'

- [`http://localhost:8000/calculate_solar_time_skyfield/?longitude=6.6327&latitude=46.5218&timestamp=2023-06-26T12:04:25&timezone=CET`](http://localhost:8000/calculate_solar_time_skyfield/?longitude=6.6327&latitude=46.5218&timestamp=2023-06-26T12:04:25&timezone=CET)

## Direct inclined irradiance

- API endpoint to calculate the direct inclined irradiance:

```
..
```

## Plot solar declination

- [Plot solar declination for 2023](http://localhost:8000/plot_solar_declination_one_year_bokeh?year=2023)

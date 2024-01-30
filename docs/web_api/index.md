---
icon: simple/fastapi
tags:
  - How-To
  - Web API
---

# Request examples

Then, demonstration of an endpoint

### Solar `time` again

- [`http://localhost:8000/calculate_solar_time_skyfield/?longitude=-70&latitude=40&timestamp=2023-06-26T12:00:00&timezone=America/New_York`](http://localhost:8000/calculate_solar_time_skyfield/?longitude=-70&latitude=40&timestamp=2023-06-26T12:00:00&timezone=America/New_York)

    - functin   : `calculate_solar_time_skyfield`
    - longitude : -70
    - latitude  : 40
    - timestamp : 2023-06-26T12:00:00
    - timezone  : 'America/New_York'

- [`http://localhost:8000/calculate_solar_time_skyfield/?longitude=6.6327&latitude=46.5218&timestamp=2023-06-26T12:04:25&timezone=CET`](http://localhost:8000/calculate_solar_time_skyfield/?longitude=6.6327&latitude=46.5218&timestamp=2023-06-26T12:04:25&timezone=CET)

### Direct inclined irradiance

- API endpoint to calculate the direct inclined irradiance:

```
..
```

### Plot solar declination

- [Plot solar declination for 2023](http://localhost:8000/plot_solar_declination_one_year_bokeh?year=2023)

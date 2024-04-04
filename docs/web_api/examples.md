---
icon: material/server-network
title: Examples
tags:
  - How-To
  - Web API
  - Examples
---

## Photovoltaic power time series

### In the browser

``` html
http://localhost:8000/calculate/power/broadband?elevation=214&start_time=2010-01-27&frequency=h&end_time=2010-01-28&random_time_series=false&temperature_series=25&wind_speed_series=0&mask_and_scale=false&tolerance=0.1&in_memory=false&dtype=float32&array_backend=NUMPY&multi_thread=true&surface_orientation=180&surface_tilt=45&linke_turbidity_factor_series=2&apply_atmospheric_refraction=true&refracted_solar_zenith=1.5853349194640094&albedo=0.2&apply_angular_loss_factor=true&solar_position_model=NOAA&solar_incidence_model=Jenco&solar_time_model=Milne1921&time_offset_global=0&hour_offset=0&solar_constant=1360.8&perigee_offset=0.048869&eccentricity_correction_factor=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&temperature_model=Faiman&verbose=0&log=0&fingerprint=false&profile=false&longitude=8.628&latitude=45.812
```

Multiple years

``` html
http://localhost:8000/calculate/power/broadband?elevation=214&start_time=2005-01-01&frequency=h&end_time=2020-12-31&random_time_series=false&temperature_series=25&wind_speed_series=0&mask_and_scale=false&tolerance=0.1&in_memory=false&dtype=float32&array_backend=NUMPY&multi_thread=true&surface_orientation=180&surface_tilt=45&linke_turbidity_factor_series=2&apply_atmospheric_refraction=true&refracted_solar_zenith=1.5853349194640094&albedo=0.2&apply_angular_loss_factor=true&solar_position_model=NOAA&solar_incidence_model=Jenco&solar_time_model=Milne1921&time_offset_global=0&hour_offset=0&solar_constant=1360.8&perigee_offset=0.048869&eccentricity_correction_factor=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&temperature_model=Faiman&verbose=0&log=0&fingerprint=false&profile=false&longitude=8&latitude=45
```

### In the command line

A single timestamp


``` bash
curl -X 'GET' \
  'http://localhost:8000/calculate/power/broadband?elevation=214&start_time=2010-01-27&frequency=h&end_time=2010-01-28&random_time_series=false&temperature_series=25&wind_speed_series=0&mask_and_scale=false&tolerance=0.1&in_memory=false&dtype=float32&array_backend=NUMPY&multi_thread=true&surface_orientation=180&surface_tilt=45&linke_turbidity_factor_series=2&apply_atmospheric_refraction=true&refracted_solar_zenith=1.5853349194640094&albedo=0.2&apply_angular_loss_factor=true&solar_position_model=NOAA&solar_incidence_model=Jenco&solar_time_model=Milne1921&time_offset_global=0&hour_offset=0&solar_constant=1360.8&perigee_offset=0.048869&eccentricity_correction_factor=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&temperature_model=Faiman&verbose=0&log=0&fingerprint=false&profile=false&longitude=8.628&latitude=45.812' \
  -H 'accept: application/json'
```


## Other examples

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

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

A single timestamp

``` html
http://127.0.0.1:8000/calculate/power/broadband?elevation=214&frequency=h&random_time_series=false&temperature_series=25&wind_speed_series=0&mask_and_scale=false&tolerance=0.1&in_memory=false&dtype=float32&array_backend=NUMPY&multi_thread=true&surface_orientation=180&surface_tilt=45&linke_turbidity_factor_series=2&apply_atmospheric_refraction=true&refracted_solar_zenith=1.5853349194640094&albedo=0.2&apply_angular_loss_factor=true&solar_position_model=NOAA&solar_incidence_model=Jenco&solar_time_model=Milne1921&time_offset_global=0&hour_offset=0&solar_constant=1360.8&perigee_offset=0.048869&eccentricity_correction_factor=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&temperature_model=Faiman&verbose=0&log=0&fingerprint=false&profile=false&longitude=8.628&latitude=45.812&timestamps=2010-01-27%2012%3A00%3A00
```

!!! danger "Understanding the Response -- Update-Me"

    Explain the structure of the API response and how to interpret it.

A day

``` html
http://localhost:8000/calculate/power/broadband?elevation=214&start_time=2010-01-27&frequency=h&end_time=2010-01-28&random_time_series=false&temperature_series=25&wind_speed_series=0&mask_and_scale=false&tolerance=0.1&in_memory=false&dtype=float32&array_backend=NUMPY&multi_thread=true&surface_orientation=180&surface_tilt=45&linke_turbidity_factor_series=2&apply_atmospheric_refraction=true&refracted_solar_zenith=1.5853349194640094&albedo=0.2&apply_angular_loss_factor=true&solar_position_model=NOAA&solar_incidence_model=Jenco&solar_time_model=Milne1921&time_offset_global=0&hour_offset=0&solar_constant=1360.8&perigee_offset=0.048869&eccentricity_correction_factor=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&temperature_model=Faiman&verbose=0&log=0&fingerprint=false&profile=false&longitude=8.628&latitude=45.812
```

A month

``` html
http://127.0.0.1:8000/calculate/power/broadband?elevation=214&start_time=2010-06-01&frequency=h&end_time=2010-07-01&random_time_series=false&temperature_series=25&wind_speed_series=0&mask_and_scale=false&tolerance=0.1&in_memory=false&dtype=float32&array_backend=NUMPY&multi_thread=true&surface_orientation=180&surface_tilt=45&linke_turbidity_factor_series=2&apply_atmospheric_refraction=true&refracted_solar_zenith=1.5853349194640094&albedo=0.2&apply_angular_loss_factor=true&solar_position_model=NOAA&solar_incidence_model=Jenco&solar_time_model=Milne1921&time_offset_global=0&hour_offset=0&solar_constant=1360.8&perigee_offset=0.048869&eccentricity_correction_factor=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&temperature_model=Faiman&verbose=0&log=0&fingerprint=false&profile=false&longitude=8.628&latitude=45.812
```

A year

``` html
curl -X 'GET' \
  'http://127.0.0.1:8000/calculate/power/broadband?elevation=214&start_time=2010-01-01&frequency=h&end_time=2010-12-31&random_time_series=false&temperature_series=25&wind_speed_series=0&mask_and_scale=false&tolerance=0.1&in_memory=false&dtype=float32&array_backend=NUMPY&multi_thread=true&surface_orientation=180&surface_tilt=45&linke_turbidity_factor_series=2&apply_atmospheric_refraction=true&refracted_solar_zenith=1.5853349194640094&albedo=0.2&apply_angular_loss_factor=true&solar_position_model=NOAA&solar_incidence_model=Jenco&solar_time_model=Milne1921&time_offset_global=0&hour_offset=0&solar_constant=1360.8&perigee_offset=0.048869&eccentricity_correction_factor=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&temperature_model=Faiman&verbose=0&log=0&fingerprint=false&profile=false&longitude=8.628&latitude=45.812' \
  -H 'accept: application/json'
```

Multiple years

``` html
http://localhost:8000/calculate/power/broadband?elevation=214&start_time=2005-01-01&frequency=h&end_time=2020-12-31&random_time_series=false&temperature_series=25&wind_speed_series=0&mask_and_scale=false&tolerance=0.1&in_memory=false&dtype=float32&array_backend=NUMPY&multi_thread=true&surface_orientation=180&surface_tilt=45&linke_turbidity_factor_series=2&apply_atmospheric_refraction=true&refracted_solar_zenith=1.5853349194640094&albedo=0.2&apply_angular_loss_factor=true&solar_position_model=NOAA&solar_incidence_model=Jenco&solar_time_model=Milne1921&time_offset_global=0&hour_offset=0&solar_constant=1360.8&perigee_offset=0.048869&eccentricity_correction_factor=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&temperature_model=Faiman&verbose=0&log=0&fingerprint=false&profile=false&longitude=8&latitude=45
```

### In the command line

A single timestamp

``` bash
curl -X 'GET' \
  'http://127.0.0.1:8000/calculate/power/broadband?elevation=214&frequency=h&random_time_series=false&temperature_series=25&wind_speed_series=0&mask_and_scale=false&tolerance=0.1&in_memory=false&dtype=float32&array_backend=NUMPY&multi_thread=true&surface_orientation=180&surface_tilt=45&linke_turbidity_factor_series=2&apply_atmospheric_refraction=true&refracted_solar_zenith=1.5853349194640094&albedo=0.2&apply_angular_loss_factor=true&solar_position_model=NOAA&solar_incidence_model=Jenco&solar_time_model=Milne1921&time_offset_global=0&hour_offset=0&solar_constant=1360.8&perigee_offset=0.048869&eccentricity_correction_factor=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&temperature_model=Faiman&verbose=0&log=0&fingerprint=false&profile=false&longitude=8.628&latitude=45.812&timestamps=2010-01-27%2012%3A00%3A00' \
  -H 'accept: application/json'
```

A day

``` bash
curl -X 'GET' \
  'http://localhost:8000/calculate/power/broadband?elevation=214&start_time=2010-01-27&frequency=h&end_time=2010-01-28&random_time_series=false&temperature_series=25&wind_speed_series=0&mask_and_scale=false&tolerance=0.1&in_memory=false&dtype=float32&array_backend=NUMPY&multi_thread=true&surface_orientation=180&surface_tilt=45&linke_turbidity_factor_series=2&apply_atmospheric_refraction=true&refracted_solar_zenith=1.5853349194640094&albedo=0.2&apply_angular_loss_factor=true&solar_position_model=NOAA&solar_incidence_model=Jenco&solar_time_model=Milne1921&time_offset_global=0&hour_offset=0&solar_constant=1360.8&perigee_offset=0.048869&eccentricity_correction_factor=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&temperature_model=Faiman&verbose=0&log=0&fingerprint=false&profile=false&longitude=8.628&latitude=45.812' \
  -H 'accept: application/json'
```

A month

``` bash
curl -X 'GET' \
  'http://127.0.0.1:8000/calculate/power/broadband?elevation=214&start_time=2010-06-01&frequency=h&end_time=2010-07-01&random_time_series=false&temperature_series=25&wind_speed_series=0&mask_and_scale=false&tolerance=0.1&in_memory=false&dtype=float32&array_backend=NUMPY&multi_thread=true&surface_orientation=180&surface_tilt=45&linke_turbidity_factor_series=2&apply_atmospheric_refraction=true&refracted_solar_zenith=1.5853349194640094&albedo=0.2&apply_angular_loss_factor=true&solar_position_model=NOAA&solar_incidence_model=Jenco&solar_time_model=Milne1921&time_offset_global=0&hour_offset=0&solar_constant=1360.8&perigee_offset=0.048869&eccentricity_correction_factor=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&temperature_model=Faiman&verbose=0&log=0&fingerprint=false&profile=false&longitude=8.628&latitude=45.812' \
  -H 'accept: application/json'
```

A year

``` bash
curl -X 'GET' \
  'http://127.0.0.1:8000/calculate/power/broadband?elevation=214&start_time=2010-01-01&frequency=h&end_time=2010-12-31&random_time_series=false&temperature_series=25&wind_speed_series=0&mask_and_scale=false&tolerance=0.1&in_memory=false&dtype=float32&array_backend=NUMPY&multi_thread=true&surface_orientation=180&surface_tilt=45&linke_turbidity_factor_series=2&apply_atmospheric_refraction=true&refracted_solar_zenith=1.5853349194640094&albedo=0.2&apply_angular_loss_factor=true&solar_position_model=NOAA&solar_incidence_model=Jenco&solar_time_model=Milne1921&time_offset_global=0&hour_offset=0&solar_constant=1360.8&perigee_offset=0.048869&eccentricity_correction_factor=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&temperature_model=Faiman&verbose=0&log=0&fingerprint=false&profile=false&longitude=8.628&latitude=45.812' \
  -H 'accept: application/json'
```

Multiple years

``` bash
curl -X 'GET' \
  'http://127.0.0.1:8000/calculate/power/broadband?elevation=214&start_time=2005-01-01&frequency=h&end_time=2020-12-31&random_time_series=false&temperature_series=25&wind_speed_series=0&mask_and_scale=false&tolerance=0.1&in_memory=false&dtype=float32&array_backend=NUMPY&multi_thread=true&surface_orientation=180&surface_tilt=45&linke_turbidity_factor_series=2&apply_atmospheric_refraction=true&refracted_solar_zenith=1.5853349194640094&albedo=0.2&apply_angular_loss_factor=true&solar_position_model=NOAA&solar_incidence_model=Jenco&solar_time_model=Milne1921&time_offset_global=0&hour_offset=0&solar_constant=1360.8&perigee_offset=0.048869&eccentricity_correction_factor=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&temperature_model=Faiman&verbose=0&log=0&fingerprint=false&profile=false&longitude=8.628&latitude=45.812' \
  -H 'accept: application/json'
```

!!! attention "How long does it take for the calculations ?"

    The multi-year example :
    
    - real	0m1,406s
    - user	0m0,013s
    - sys	0m0,000s

## Reading time series data

A year

``` bash
curl -X 'GET' \
  'http://127.0.0.2:8000/calculate/power/broadband?elevation=214&start_time=2005-01-01&frequency=h&end_time=2005-12-31&global_horizontal_irradiance=%2Fspacetime%2Fpvgis%2Fpvgis-prototype%2Fdocs%2Fdata%2Fsarah2_sis_over_esti_jrc.nc&direct_horizontal_irradiance=%2Fspacetime%2Fpvgis%2Fpvgis-prototype%2Fdocs%2Fdata%2Fsarah2_sid_over_esti_jrc.nc&temperature_series=%2Fspacetime%2Fpvgis%2Fpvgis-prototype%2Fdocs%2Fdata%2Fera5_t2m_over_esti_jrc.nc&wind_speed_series=%2Fspacetime%2Fpvgis%2Fpvgis-prototype%2Fdocs%2Fdata%2Fera5_ws2m_over_esti_jrc.nc&mask_and_scale=false&tolerance=0.1&in_memory=false&dtype=float32&array_backend=NUMPY&multi_thread=true&surface_orientation=180&surface_tilt=45&linke_turbidity_factor_series=2&apply_atmospheric_refraction=true&refracted_solar_zenith=1.5853349194640094&albedo=0.2&apply_angular_loss_factor=true&solar_position_model=NOAA&solar_incidence_model=Jenco&solar_time_model=Milne1921&time_offset_global=0&hour_offset=0&solar_constant=1360.8&perigee_offset=0.048869&eccentricity_correction_factor=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&temperature_model=Faiman&verbose=0&log=0&fingerprint=false&profile=false&csv=false&longitude=8.628&latitude=45.812' \
  -H 'accept: application/json'
```

## Error Handling

!!! danger 

    [Discuss common errors and how to handle them.]

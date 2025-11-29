---
icon: material/server-network
title: Examples
tags:
  - How-To
  - Web API
  - Examples
---

## Photovoltaic power

The following examples query the `/power/broadband` endpoint for photovoltaic power calculations.
Each demonstrates a different time range - from single timestamps to multi-year analyses.

!!! tip "Try in Browser"

    Copy any URL and paste directly into your browser's address bar
    while the server is running.
    Alternatively,
    we can use `curl` to query a running Web API server as in the examples below :

**A single timestamp**

In the browser

``` html
http://127.0.0.2:8000/power/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&timestamps=2010-01-27%2012%3A00%3A00&frequency=Hourly&timezone=UTC&neighbor_lookup=nearest&tolerance=0.1&mask_and_scale=false&in_memory=false&linke_turbidity_factor_series=2&albedo=0.2&apply_reflectivity_factor=true&solar_position_model=NOAA&solar_incidence_model=Iqbal&horizon_profile=None&shading_model=PVGIS&zero_negative_solar_incidence_angle=true&solar_time_model=Milne1921&solar_constant=1360.8&eccentricity_phase_offset=0.048869&eccentricity_amplitude=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&temperature_model=Faiman&radiation_cutoff_threshold=0&angle_output_units=Radians&statistics=false&groupby=None&verbose=0&quiet=false&fingerprint=false&quick_response_code=None&surface_position_optimisation_mode=None&surface_position_optimisation_method=L-BFGS-B&shgo_sampling_method=sobol&number_of_sampling_points=100&iterations=20
```

or in the command line

``` bash
curl -X 'GET' 'http://127.0.0.2:8000/power/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&timestamps=2010-01-27%2012%3A00%3A00&frequency=Hourly&timezone=UTC&neighbor_lookup=nearest&tolerance=0.1&mask_and_scale=false&in_memory=false&linke_turbidity_factor_series=2&albedo=0.2&apply_reflectivity_factor=true&solar_position_model=NOAA&solar_incidence_model=Iqbal&horizon_profile=None&shading_model=PVGIS&zero_negative_solar_incidence_angle=true&solar_time_model=Milne1921&solar_constant=1360.8&eccentricity_phase_offset=0.048869&eccentricity_amplitude=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&temperature_model=Faiman&radiation_cutoff_threshold=0&angle_output_units=Radians&statistics=false&groupby=None&verbose=0&quiet=false&fingerprint=false&quick_response_code=None&surface_position_optimisation_mode=None&surface_position_optimisation_method=L-BFGS-B&shgo_sampling_method=sobol&number_of_sampling_points=100&iterations=20' -H 'accept: application/json'
```


**A day**

``` html
http://127.0.0.2:8000/power/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2010-01-27&end_time=2010-01-28&frequency=Hourly&timezone=UTC&neighbor_lookup=nearest&tolerance=0.1&mask_and_scale=false&in_memory=false&linke_turbidity_factor_series=2&albedo=0.2&apply_reflectivity_factor=true&solar_position_model=NOAA&solar_incidence_model=Iqbal&horizon_profile=None&shading_model=PVGIS&zero_negative_solar_incidence_angle=true&solar_time_model=Milne1921&solar_constant=1360.8&eccentricity_phase_offset=0.048869&eccentricity_amplitude=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&temperature_model=Faiman&radiation_cutoff_threshold=0&angle_output_units=Radians&statistics=false&groupby=None&verbose=0&quiet=false&fingerprint=false&quick_response_code=None&surface_position_optimisation_mode=None&surface_position_optimisation_method=L-BFGS-B&shgo_sampling_method=sobol&number_of_sampling_points=100&iterations=20
```

or

``` bash
curl -X 'GET' \
  'http://127.0.0.2:8000/power/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2010-01-27&end_time=2010-01-28&frequency=Hourly&timezone=UTC&neighbor_lookup=nearest&tolerance=0.1&mask_and_scale=false&in_memory=false&linke_turbidity_factor_series=2&albedo=0.2&apply_reflectivity_factor=true&solar_position_model=NOAA&solar_incidence_model=Iqbal&horizon_profile=None&shading_model=PVGIS&zero_negative_solar_incidence_angle=true&solar_time_model=Milne1921&solar_constant=1360.8&eccentricity_phase_offset=0.048869&eccentricity_amplitude=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&temperature_model=Faiman&radiation_cutoff_threshold=0&angle_output_units=Radians&statistics=false&groupby=None&verbose=0&quiet=false&fingerprint=false&quick_response_code=None&surface_position_optimisation_mode=None&surface_position_optimisation_method=L-BFGS-B&shgo_sampling_method=sobol&number_of_sampling_points=100&iterations=20' \
  -H 'accept: application/json'
```

**A month**

``` html
http://127.0.0.2:8000/power/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2010-06-01&end_time=2010-07-01&frequency=Hourly&timezone=UTC&neighbor_lookup=nearest&tolerance=0.1&mask_and_scale=false&in_memory=false&linke_turbidity_factor_series=2&albedo=0.2&apply_reflectivity_factor=true&solar_position_model=NOAA&solar_incidence_model=Iqbal&horizon_profile=None&shading_model=PVGIS&zero_negative_solar_incidence_angle=true&solar_time_model=Milne1921&solar_constant=1360.8&eccentricity_phase_offset=0.048869&eccentricity_amplitude=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&temperature_model=Faiman&radiation_cutoff_threshold=0&angle_output_units=Radians&statistics=false&groupby=None&verbose=0&quiet=false&fingerprint=false&quick_response_code=None&surface_position_optimisation_mode=None&surface_position_optimisation_method=L-BFGS-B&shgo_sampling_method=sobol&number_of_sampling_points=100&iterations=20
```

or

``` bash
curl -X 'GET' \
  'http://127.0.0.2:8000/power/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2010-06-01&end_time=2010-07-01&frequency=Hourly&timezone=UTC&neighbor_lookup=nearest&tolerance=0.1&mask_and_scale=false&in_memory=false&linke_turbidity_factor_series=2&albedo=0.2&apply_reflectivity_factor=true&solar_position_model=NOAA&solar_incidence_model=Iqbal&horizon_profile=None&shading_model=PVGIS&zero_negative_solar_incidence_angle=true&solar_time_model=Milne1921&solar_constant=1360.8&eccentricity_phase_offset=0.048869&eccentricity_amplitude=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&temperature_model=Faiman&radiation_cutoff_threshold=0&angle_output_units=Radians&statistics=false&groupby=None&verbose=0&quiet=false&fingerprint=false&quick_response_code=None&surface_position_optimisation_mode=None&surface_position_optimisation_method=L-BFGS-B&shgo_sampling_method=sobol&number_of_sampling_points=100&iterations=20' \
  -H 'accept: application/json'
```

**A year**

``` html
  'http://127.0.0.2:8000/power/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2010-01-01&end_time=2011-01-01&frequency=Hourly&timezone=UTC&neighbor_lookup=nearest&tolerance=0.1&mask_and_scale=false&in_memory=false&linke_turbidity_factor_series=2&albedo=0.2&apply_reflectivity_factor=true&solar_position_model=NOAA&solar_incidence_model=Iqbal&horizon_profile=None&shading_model=PVGIS&zero_negative_solar_incidence_angle=true&solar_time_model=Milne1921&solar_constant=1360.8&eccentricity_phase_offset=0.048869&eccentricity_amplitude=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&temperature_model=Faiman&radiation_cutoff_threshold=0&angle_output_units=Radians&statistics=false&groupby=None&verbose=0&quiet=false&fingerprint=false&quick_response_code=None&surface_position_optimisation_mode=None&surface_position_optimisation_method=L-BFGS-B&shgo_sampling_method=sobol&number_of_sampling_points=100&iterations=20' \
```

or

``` bash
curl -X 'GET' \
  'http://127.0.0.2:8000/power/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2010-01-01&end_time=2011-01-01&frequency=Hourly&timezone=UTC&neighbor_lookup=nearest&tolerance=0.1&mask_and_scale=false&in_memory=false&linke_turbidity_factor_series=2&albedo=0.2&apply_reflectivity_factor=true&solar_position_model=NOAA&solar_incidence_model=Iqbal&horizon_profile=None&shading_model=PVGIS&zero_negative_solar_incidence_angle=true&solar_time_model=Milne1921&solar_constant=1360.8&eccentricity_phase_offset=0.048869&eccentricity_amplitude=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&temperature_model=Faiman&radiation_cutoff_threshold=0&angle_output_units=Radians&statistics=false&groupby=None&verbose=0&quiet=false&fingerprint=false&quick_response_code=None&surface_position_optimisation_mode=None&surface_position_optimisation_method=L-BFGS-B&shgo_sampling_method=sobol&number_of_sampling_points=100&iterations=20' \
  -H 'accept: application/json'
```

**Multiple years**

``` html
http://127.0.0.2:8000/power/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2005-01-01&end_time=2021-01-01&frequency=Hourly&timezone=UTC&neighbor_lookup=nearest&tolerance=0.1&mask_and_scale=false&in_memory=false&linke_turbidity_factor_series=2&albedo=0.2&apply_reflectivity_factor=true&solar_position_model=NOAA&solar_incidence_model=Iqbal&horizon_profile=None&shading_model=PVGIS&zero_negative_solar_incidence_angle=true&solar_time_model=Milne1921&solar_constant=1360.8&eccentricity_phase_offset=0.048869&eccentricity_amplitude=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&temperature_model=Faiman&radiation_cutoff_threshold=0&angle_output_units=Radians&statistics=false&groupby=None&verbose=0&quiet=false&fingerprint=false&quick_response_code=None&surface_position_optimisation_mode=None&surface_position_optimisation_method=L-BFGS-B&shgo_sampling_method=sobol&number_of_sampling_points=100&iterations=20
```

or

``` bash
curl -X 'GET' \
  'http://127.0.0.2:8000/power/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2005-01-01&end_time=2021-01-01&frequency=Hourly&timezone=UTC&neighbor_lookup=nearest&tolerance=0.1&mask_and_scale=false&in_memory=false&linke_turbidity_factor_series=2&albedo=0.2&apply_reflectivity_factor=true&solar_position_model=NOAA&solar_incidence_model=Iqbal&horizon_profile=None&shading_model=PVGIS&zero_negative_solar_incidence_angle=true&solar_time_model=Milne1921&solar_constant=1360.8&eccentricity_phase_offset=0.048869&eccentricity_amplitude=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&temperature_model=Faiman&radiation_cutoff_threshold=0&angle_output_units=Radians&statistics=false&groupby=None&verbose=0&quiet=false&fingerprint=false&quick_response_code=None&surface_position_optimisation_mode=None&surface_position_optimisation_method=L-BFGS-B&shgo_sampling_method=sobol&number_of_sampling_points=100&iterations=20' \
  -H 'accept: application/json'
```

!!! attention "How long does it take for the calculations ?"

    The multi-year example :
    
    Request duration
    ```
    1056 ms
    ```

## Photovoltaic performance analysis

In the command line

``` bash
curl -X 'GET' \
  'http://127.0.0.2:8000/performance/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2013-01-01&end_time=2013-12-31&frequency=Hourly&timezone=UTC&neighbor_lookup=nearest&tolerance=0.1&mask_and_scale=false&in_memory=false&linke_turbidity_factor_series=2&albedo=0.2&apply_reflectivity_factor=true&solar_position_model=NOAA&solar_incidence_model=Iqbal&horizon_profile=None&shading_model=PVGIS&zero_negative_solar_incidence_angle=true&solar_time_model=Milne1921&solar_constant=1360.8&eccentricity_phase_offset=0.048869&eccentricity_amplitude=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&temperature_model=Faiman&radiation_cutoff_threshold=0&angle_output_units=Radians&analysis=Simple&statistics=false&groupby=None&verbose=0&index=false&quiet=false&fingerprint=false&quick_response_code=None&metadata=false&surface_position_optimisation_mode=None&surface_position_optimisation_method=L-BFGS-B&shgo_sampling_method=sobol&number_of_sampling_points=100&iterations=20' \
  -H 'accept: application/json'
```

There are many options to set.
For example, requesting for an detailed results takes to set the corresponding parameter `analysis=Extended`

``` bash
curl -X 'GET' \
  'http://127.0.0.2:8000/performance/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2013-01-01&end_time=2013-12-31&frequency=Hourly&timezone=UTC&neighbor_lookup=nearest&tolerance=0.1&mask_and_scale=false&in_memory=false&linke_turbidity_factor_series=2&albedo=0.2&apply_reflectivity_factor=true&solar_position_model=NOAA&solar_incidence_model=Iqbal&horizon_profile=None&shading_model=PVGIS&zero_negative_solar_incidence_angle=true&solar_time_model=Milne1921&solar_constant=1360.8&eccentricity_phase_offset=0.048869&eccentricity_amplitude=0.03344&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&temperature_model=Faiman&radiation_cutoff_threshold=0&angle_output_units=Radians&analysis=Extended&statistics=false&groupby=None&verbose=0&index=false&quiet=false&fingerprint=false&quick_response_code=None&metadata=false&surface_position_optimisation_mode=None&surface_position_optimisation_method=L-BFGS-B&shgo_sampling_method=sobol&number_of_sampling_points=100&iterations=20' \
  -H 'accept: application/json'
```

!!! note "Level of analysis"

    Checkout for the `analysis` parameter.

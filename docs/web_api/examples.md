---
icon: material/server-network
title: Examples
tags:
  - How-To
  - Web API
  - Examples
---


## Overview

<div class="grid cards" markdown>


  | Endpoint                                                                                                                                     | Description                                                                       |
  |----------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
  | :octicons-command-palette-24: [performance/broadband-->](http://127.0.0.1:8001/docs#/Performance/performance-broadband){ .lg .middle }       |🔌Get the analysis of the photovoltaic performance                                 |
  | :octicons-command-palette-24: [power/broadband-->](http://127.0.0.1:8001/docs#/Power/power-broadband)                                        |🔌 Get the photovoltaic power output                                               |
  | :octicons-command-palette-24: [power/broadband-multiple-surfaces-->](http://127.0.0.1:8001/docs#/Power/power-broadband-multiple-surfaces)    |🔌 Get the photovoltaic power output over multiple surfaces                        |
  | :octicons-command-palette-24: [power/surface-position-optimisation-->](http://127.0.0.1:8001/docs#/Power/surface-position-optimisation)      | 📐 Get the optimal surface position for a photovoltaic module                     |
  | :octicons-command-palette-24: [solar-position/overview-->](http://127.0.0.1:8001/docs#/Solar-Position/overview)                              | :material-sun-angle: Get solar position parameters                                |
  | [**and more...**](http://127.0.0.1:8001/docs#/) |

</div>

!!! tip "Running the Web API Locally"

    **The above links open the Web API locally using port `8001`.**  
    To learn how to set up a local instance, check [this guide](run.md).

    You can open a `uvicorn` instance on port 8001 by running:
    
    ```bash
    uvicorn pvgisprototype.webapi:app --port 8001 --reload
    ```

## Photovoltaic performance

### Using the documentation page

Using the documentation page you can navigate and play with the currently available endpoints and the respective responses as in the example bellow.

<video style="width:100%" muted="True" controls="" alt="type:video">
   <source src="/videos/perfomance_small.mp4" type="video/mp4">
</video>


### In the browser


A complete day

``` html
http://127.0.0.1:8001/performance/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2013-01-01%2000%3A00%3A00&end_time=2013-01-01%2023%3A00%3A00&frequency=Hourly&timezone=UTC&horizon_profile=PVGIS&shading_model=PVGIS&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&angle_output_units=Radians&analysis=Simple&verbose=0&index=false&quiet=false&fingerprint=false&quick_response_code=None&metadata=false
```

A month

``` html
http://127.0.0.1:8001/performance/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2013-01-01%2000%3A00%3A00&end_time=2013-01-31%2023%3A00%3A00&frequency=Hourly&timezone=UTC&horizon_profile=PVGIS&shading_model=PVGIS&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&angle_output_units=Radians&analysis=Simple&verbose=0&index=false&quiet=false&fingerprint=false&quick_response_code=None&metadata=false
```

A year

``` html
http://127.0.0.1:8001/performance/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2013-01-01%2000%3A00%3A00&end_time=2013-12-31%2023%3A00%3A00&frequency=Hourly&timezone=UTC&horizon_profile=PVGIS&shading_model=PVGIS&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&angle_output_units=Radians&analysis=Simple&verbose=0&index=false&quiet=false&fingerprint=false&quick_response_code=None&metadata=false
```

Multiple years

``` html
http://127.0.0.1:8001/performance/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2005-01-01&end_time=2020-12-31&frequency=Hourly&timezone=UTC&horizon_profile=PVGIS&shading_model=PVGIS&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&angle_output_units=Radians&analysis=Simple&verbose=0&index=false&quiet=false&fingerprint=false&quick_response_code=None&metadata=false
```

### In the command line

A day

``` bash
curl -X 'GET' \
  'http://127.0.0.1:8001/performance/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2013-01-01%2000%3A00%3A00&end_time=2013-01-01%2023%3A00%3A00&frequency=Hourly&timezone=UTC&horizon_profile=PVGIS&shading_model=PVGIS&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&angle_output_units=Radians&analysis=Simple&verbose=0&index=false&quiet=false&fingerprint=false&quick_response_code=None&metadata=false' \
  -H 'accept: application/json'
```

A month

``` bash
curl -X 'GET' \
  'http://127.0.0.1:8001/performance/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2013-01-01%2000%3A00%3A00&end_time=2013-01-31%2023%3A00%3A00&frequency=Hourly&timezone=UTC&horizon_profile=PVGIS&shading_model=PVGIS&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&angle_output_units=Radians&analysis=Simple&verbose=0&index=false&quiet=false&fingerprint=false&quick_response_code=None&metadata=false' \
  -H 'accept: application/json'
```

A year

``` bash
curl -X 'GET' \
  'http://127.0.0.1:8001/performance/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2013-01-01%2000%3A00%3A00&end_time=2013-12-31%2023%3A00%3A00&frequency=Hourly&timezone=UTC&horizon_profile=PVGIS&shading_model=PVGIS&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&angle_output_units=Radians&analysis=Simple&verbose=0&index=false&quiet=false&fingerprint=false&quick_response_code=None&metadata=false' \
  -H 'accept: application/json'
```

Multiple years

``` bash
curl -X 'GET' \
  'http://127.0.0.1:8001/performance/broadband?longitude=8.628&latitude=45.812&elevation=214&surface_orientation=180&surface_tilt=45&start_time=2005-01-01&end_time=2020-12-31&frequency=Hourly&timezone=UTC&horizon_profile=PVGIS&shading_model=PVGIS&photovoltaic_module=cSi%3AFree%20standing&system_efficiency=0.86&power_model=Huld%202011&peak-power=1&angle_output_units=Radians&analysis=Simple&verbose=0&index=false&quiet=false&fingerprint=false&quick_response_code=None&metadata=false' \
  -H 'accept: application/json'
```

!!! attention "How long does it take for the calculations ?"

    The multi-year example using the following hardware:

    | Component   | Details |
    |------------|---------|
    | **CPU**    | 12th Gen Intel(R) Core(TM) i7-12700H 4.60 GHz|
    | **RAM**    | 40GB DDR5 4800MHz |
    | **Storage** | 512GB M.2 2280, NVMe PCIe 4.0, Read: ~3,500 MB/s Write: ~3,000 MB/s|
    | **OS**     | Ubuntu 22.04 LTS (kernel 5.15) |
    | **Python Version** | 3.11.11 |
    | **Frameworks** | FastAPI 0.112,2, Uvicorn 0.30.6 |

    The response time is:
            
    ```bash
    real    0m0.706s
    user    0m0.011s
    sys     0m0.001s
    ```

## Error Handling

Bellow you will find an analytical table with possible errors that can be returned in an web API call.

| Code   | Explanation           | Description                                                             |
|--------|-----------------------|-------------------------------------------------------------------------|
| `200`  | Success               | The request was successful.                                             |
| `400`  | Bad Request           | The endpoint rejected the request due to incorrect inputs.              |
| `404`  | Not Available         | The service is not available.                                           |
| `429`  | Too Many Requests     | Too many requests.                                                      |
| `450`  | Data Unreachable      | The data are unreachable.                                               |
| `460`  | Service Unreachable   | The web API services are unreachable.                                   |
| `500`  | Server Error          | Something went wrong on our end; if it persists, send a help ticket.    |
| `502`  | Bad Gateway           | Something went wrong; if it persists, send a help ticket.               |
| `504`  | Gateway Timeout       | Something went wrong; if it persists, send a help ticket.               |
| `550`  | Data Issue            | An error occurred reading the data; if it persists, send a help ticket. |

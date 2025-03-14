---
icon: material/eye
title: Overview
tags:
  - Overview
  - Data
  - Time Series
  - Chunking
  - Chunked Data
  - Chunks
  - Solar Irradiance
  - Global Horizontal Irradiance
  - Direct Horizontal Irradiance
  - Spectral Factor
  - Temperature
  - Wind Speed
---

This reference page comprises all about the time series data that power PVGIS :

1. overview of the **input time series**
2. **pre-processing** to generate Zarr stores
3. assessing the **reading performance**
4. testing PVGIS' **scalability**

# Time series

PVGIS
can work as a clear-sky simulation engine
as well as analyse the performance of a photovoltaic system
based on external time series data
for solar irradiance
and important meteorological variables alike.

The default set of input time series
that power the calculations of the public Web application,
and the Web API as well,
is :

- Solar irradiance time series from the SARAH2/3 climate data records
- 🌡 Temperature at 2m height from ERA5
- 🌬 Wind speed at 10m heiht from ERA5
- :simple-spectrum: Spectral factor series for 2013, equally used for every other year, produced
  by Thomas Huld in collaboration with the German Weather Service (DWD).

```python exec="true" html="true"
--8<-- "docs/reference/time_series_data_input_diagram.py"
```

# Chunked data

```python exec="true" html="true"
--8<-- "docs/reference/time_series_chunked_data_diagram.py"
```

# Zarr stores

```python exec="true" html="true"
--8<-- "docs/reference/time_series_data_preprocessing_diagram.py"
```

# Reading performance

# Scalability


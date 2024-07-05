---
icon: simple/databricks
title: Time Series Data
tags:
  - Data
  - Time Series
  - Solar Irradiance
  - Global Horizontal Irradiance
  - Direct Horizontal Irradiance
  - Spectral Factor
  - Temperature
  - Wind Speed
---

PVGIS works both as clear-sky simulation engine as well as analysing the
performance of a photovoltaic system based on external time series data for
solar irradiance and important meteorological variables alike.

The default set of input time series that power the calculations of the public Web
application, and the Web API as well, is :

- Solar irradiance time series from the SARAH2/3 climate data records
- Temperature at 2m height from ERA5
- Wind speed at 10m heiht from ERA5
- Spectral factor series for 2013, equally used for every other year, produced
  by Thomas Huld and ... in collaboration with ...

## Input time series

```python exec="true" html="true"
--8<-- "docs/reference/time_series_data_input_diagram.py"
```

## Reading time series

How does PVGIS 6 read external time series ?

### Master-Plan

#### Pre-Process

```python exec="true" html="true"
--8<-- "docs/reference/time_series_data_preprocessing_diagram.py"
```

#### Read

```python exec="true" html="true"
--8<-- "docs/reference/time_series_data_reading_diagram.py"
```

### Alternative 1

!!! warning
    
    Storage-wise more costly

```python exec="true" html="true"
--8<-- "docs/reference/time_series_data_reading_alternative_diagram.py"
```

### Alternative 2

!!! danger
    
    Storage-wise even more costly

```python exec="true" html="true"
--8<-- "docs/reference/time_series_data_reading_alternative_2_diagram.py"
```

## A to Ω

```python exec="true" html="true"
--8<-- "docs/reference/time_series_data_from_alpha_to_omega_diagram.py"
```

### A to Ω : Horizontally

Same diagram "From A to Ω" with a horizontal layout

```python exec="true" html="true"
--8<-- "docs/reference/time_series_data_from_alpha_to_omega_alternative_diagram.py"
```

### Icons

- sun by Jolan Soens from <a href="https://thenounproject.com/browse/icons/term/sun/" target="_blank" title="sun Icons">Noun Project</a> (CC BY 3.0)

- transmission control protocol by bsd studio from <a href="https://thenounproject.com/browse/icons/term/transmission-control-protocol/" target="_blank" title="transmission control protocol Icons">Noun Project</a> (CC BY 3.0)

- time series by Christina Barysheva from <a href="https://thenounproject.com/browse/icons/term/time-series/" target="_blank" title="time series Icons">Noun Project</a> (CC BY 3.0)

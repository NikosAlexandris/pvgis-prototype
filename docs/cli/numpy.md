---
icon: custom/data-array
title: Array Computing
tags:
  - CLI
  - NumPy
  - Data Type
  - Array Backend
  - Precision
---

PVGIS makes it easy to
select among different _array backends_ and _floating point precision_.
For example,
really massive time series 
may be processed in a distributed computing context.
**Using PVGIS with the default array-backend options,
an end-user does not need to do anything.**
He can, however,
request for another array-backend
for all operations.

!!! info "Default array backend and data type"

    ```python exec="true" session="azimuth-series"
    
    from pvgisprototype.constants import DATA_TYPE_DEFAULT # markdown-exec: hide
    
    print(f'{DATA_TYPE_DEFAULT=}\n')
    
    from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT # markdown-exec: hide
    print(f'{ARRAY_BACKEND_DEFAULT=}')
    
    ```

## Array backend

!!! danger "Under development"

    The backend-agnostic array system is yet incomplete!

## :material-decimal-increase: Higher precision

While the default output is of type `float32`

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 180 45 \
    '2010-01-27 12:00:00'
```
if we ever need higher precision,
we can ask for `float64` through

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 180 45 \
    '2010-01-27 12:00:00' \
    --dtype float64
```

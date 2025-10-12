---
icon: simple/spectrum
title: Photovoltaic power
subtitle: Estimate photovoltaic performance over a time series based on broadband irradiance
tags:
  - How-To
  - API
  - Core API
  - Python API
  - Photovoltaic Performance
  - Broadband Irradiance
---

Using the API,
or indeed the CLI interface in a programmatic way,
however,
we can generate photovoltaic power series.

To do so,
we need to define the location and time of interest,
import some PVGIS-native data classes
and naturally the corresponding API or CLI functions.

Following is a how-to example,
using however an interactive `i`/`python` session.
So, it's recommended to launch an ipython interpreter :

``` bash
ipython
```

and follow along.

!!! tip "Rich output"

    `rich` is installed by default along with PVGIS.
    In case, however, it isn't installed,
    you may want to install it for a great visual experience
    when printing out Python objects.

    ``` bash
    pip install rich
    ```

First, import the `print` function from the `rich` library.
This will prettify our output !

```pycon exec="true" session="power-series" source="material-block"
  >>> from rich import print
```

## Where ?

Define the geographic location and the positioning of our solar surface

```pycon exec="true" session="power-series" source="material-block"
>>> latitude = 1
>>> longitude = 1
>>> elevation = 214
>>> surface_orientation = 1
>>> surface_tilt = 1
```

## When ?

Prepate a series of timestamps as a Pandas DatetimeIndex,
using _our_ helper function `generate_datetime_series`

```pycon exec="true" session="power-series" source="material-block"
>>> from pvgisprototype.api.datetime.datetimeindex import generate_datetime_series


>>> timestamps = generate_datetime_series(start_time="2010-01-27 08:00:00", end_time="2010-01-27 18:00:00", frequency="h")
```

and the default UTC timezone as a `ZoneInfo` object

```pycon exec="true" session="power-series" source="material-block"
>>> from zoneinfo import ZoneInfo


>>> utc_zone = ZoneInfo("UTC")
```

Let's confirm the generation of the timestamps and the timezone :

```pycon exec="true" session="power-series" source="material-block"
>>> print(f'{timestamps=}')
>>> print(f'\n{utc_zone=}')
```

## Important parameters

First, import required modules and custom data classes

Linke turbidity

```pycon exec="true" session="power-series" source="material-block"
>>> from pvgisprototype import LinkeTurbidityFactor


>>> linke_turbidity_factor_series = LinkeTurbidityFactor(value=1)
```

Type of the photovoltaic module

```pycon exec="true" session="power-series" source="material-block"
>>> from pvgisprototype.algorithms.huld.photovoltaic_module import PhotovoltaicModuleModel


>>> photovoltaic_module = PhotovoltaicModuleModel.CIS_FREE_STANDING
```

Temperature and Wind Speed

```pycon exec="true" session="power-series" source="material-block"
>>> from pvgisprototype import TemperatureSeries, WindSpeedSeries

>>> temperature_series = TemperatureSeries(value=14)
>>> wind_speed_series = WindSpeedSeries(value=0)
```

Spectral factor series

```pycon exec="true" session="power-series" source="material-block"
>>> from pvgisprototype import SpectralFactorSeries

>>> spectral_factor_series=SpectralFactorSeries(value=1)
```

## Power

Now we can use the API function `calculate_photovoltaic_power_output_series` :

```pycon exec="true" session="power-series" source="material-block"
>>> from pvgisprototype.api.power.broadband import (calculate_photovoltaic_power_output_series)

>>> power = calculate_photovoltaic_power_output_series(
>>>     longitude=longitude,
>>>     latitude=latitude,
>>>     elevation=elevation,
>>>     surface_orientation=surface_orientation,
>>>     surface_tilt=surface_tilt,
>>>     timestamps=timestamps,
>>>     timezone=utc_zone,
>>>     linke_turbidity_factor_series=linke_turbidity_factor_series,
>>>     photovoltaic_module=photovoltaic_module,
>>>     spectral_factor_series=spectral_factor_series,
>>>     temperature_series=temperature_series,
>>>     wind_speed_series=wind_speed_series,
>>> )
```

Inspect the `power` output

```pycon exec="true" session="power-series" source="material-block"
>>> print(f'{power=}')
```

or indeed, some of the inner components

```pycon exec="true" session="power-series" source="material-block"
>>> print(f'Photovoltaic power series : {power.value}')
```

```pycon exec="true" session="power-series" source="material-block"
>>> print(f'Photovoltaic power components : {power.components}')
```

## Verbosity

With extra verbosity, which means more details

### Level 1

Set `verbosity=1`

```pycon exec="true" session="power-series" source="material-block"
>>> power = calculate_photovoltaic_power_output_series(
>>>     longitude=longitude,
>>>     latitude=latitude,
>>>     elevation=elevation,
>>>     surface_orientation=surface_orientation,
>>>     surface_tilt=surface_tilt,
>>>     timestamps=timestamps,
>>>     timezone=utc_zone,
>>>     linke_turbidity_factor_series=linke_turbidity_factor_series,
>>>     photovoltaic_module=photovoltaic_module,
>>>     spectral_factor_series=spectral_factor_series,
>>>     temperature_series=temperature_series,
>>>     wind_speed_series=wind_speed_series,
>>>     verbose=1,  # or 2 or 3 and so on...
>>> )
```

and again inspect the `power` output

```pycon exec="true" session="power-series" source="material-block"
>>> print(f'{power=}')
```

### Level 2 and 3

```pycon exec="true" session="power-series" source="material-block"
>>> power_2 = calculate_photovoltaic_power_output_series(
>>>     longitude=longitude,
>>>     latitude=latitude,
>>>     elevation=elevation,
>>>     surface_orientation=surface_orientation,
>>>     surface_tilt=surface_tilt,
>>>     timestamps=timestamps,
>>>     timezone=utc_zone,
>>>     linke_turbidity_factor_series=linke_turbidity_factor_series,
>>>     photovoltaic_module=photovoltaic_module,
>>>     spectral_factor_series=spectral_factor_series,
>>>     temperature_series=temperature_series,
>>>     wind_speed_series=wind_speed_series,
>>>     verbose=2,  # or 2 or 3 and so on...
>>> )
```

```pycon exec="true" session="power-series" source="material-block"
>>> power_3 = calculate_photovoltaic_power_output_series(
>>>     longitude=longitude,
>>>     latitude=latitude,
>>>     elevation=elevation,
>>>     surface_orientation=surface_orientation,
>>>     surface_tilt=surface_tilt,
>>>     timestamps=timestamps,
>>>     timezone=utc_zone,
>>>     linke_turbidity_factor_series=linke_turbidity_factor_series,
>>>     photovoltaic_module=photovoltaic_module,
>>>     spectral_factor_series=spectral_factor_series,
>>>     temperature_series=temperature_series,
>>>     wind_speed_series=wind_speed_series,
>>>     verbose=2,  # or 2 or 3 and so on...
>>> )
```

```pycon exec="true" session="power-series" source="material-block"
>>> print(f'{power_2=}')
>>> print(f'{power_3=}')
```

!!! seealso "Verbosity"

    [Verbosity](../cli/verbosity.md)

## All in one

The easier way to replicate the above examples is an all-in-one code-block :

```pycon exec="true" session="power-series-all-in-one" source="material-block"
>>> from pvgisprototype.api.datetime.datetimeindex import generate_datetime_series
>>> from zoneinfo import ZoneInfo
>>> from pvgisprototype import LinkeTurbidityFactor
>>> from pvgisprototype import TemperatureSeries, WindSpeedSeries
>>> from pvgisprototype import SpectralFactorSeries
>>> from pvgisprototype.algorithms.huld.photovoltaic_module import PhotovoltaicModuleModel
>>> from pvgisprototype.api.power.broadband import calculate_photovoltaic_power_output_series

>>> latitude = 1
>>> longitude = 1
>>> elevation = 214
>>> surface_orientation = 1
>>> surface_tilt = 1
>>> timestamps = generate_datetime_series(start_time="2010-01-27 08:00:00", end_time="2010-01-27 18:00:00", frequency="h")
>>> utc_zone = ZoneInfo("UTC")

>>> linke_turbidity_factor_series = LinkeTurbidityFactor(value=1)
>>> photovoltaic_module = PhotovoltaicModuleModel.CIS_FREE_STANDING
>>> temperature_series = TemperatureSeries(value=14)
>>> wind_speed_series = WindSpeedSeries(value=0)
>>> spectral_factor_series=SpectralFactorSeries(value=1)

>>> power = calculate_photovoltaic_power_output_series(
>>>     longitude=longitude,
>>>     latitude=latitude,
>>>     elevation=elevation,
>>>     surface_orientation=surface_orientation,
>>>     surface_tilt=surface_tilt,
>>>     timestamps=timestamps,
>>>     timezone=utc_zone,
>>>     linke_turbidity_factor_series=linke_turbidity_factor_series,
>>>     photovoltaic_module=photovoltaic_module,
>>>     spectral_factor_series=spectral_factor_series,
>>>     temperature_series=temperature_series,
>>>     wind_speed_series=wind_speed_series,
>>> )
>>> print(f'{power=}')
```

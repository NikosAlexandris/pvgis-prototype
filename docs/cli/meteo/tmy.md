---
icon: material/weather-partly-rainy
title: TMY
tags:
  - CLI
  - Typical Meteorological Year
  - TMY
---

!!! warning "Min & Max Temperature"

    The typical _Minimum_ and _Maximum_ Dry Bulb Temperature profiles
    are usually not included in a TMY !

!!! danger "Pending completion"

    The TMY engine is pending completion to include the following variables :
    diffuse horizontal irradiance_,
    infrared radiation downwards_,
    wind direction_ and _surface pressure_.

`#!bash pvgis-prototype`
can calculate the Typical Meteorological Year
for a given location based on multi-annual
set of solar irradiance 

``` bash exec="true" result="ansi" source="above"
pvgis-prototype meteo tmy \
8.628 45.812 \
--start-time '2005-01-01' \
--end-time '2020-12-31' \
--temperature-series era5_t2m_over_esti_jrc.nc \
--neighbor-lookup nearest \
--plot-statistic TMY \
--wind-speed-series era5_ws2m_over_esti_jrc.nc \
--global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc \
--direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc \
--relative-humidity-series era5_rh_over_esti_jrc.nc \
--wind-speed-series era5_ws2m_over_esti_jrc.nc \
-v
```

Newly generated plots are saved in the current working directory.

#### Direct Normal Irradiance

<figure markdown="span">
  ![Typical Yearly Direct Normal Irradiance](pvgis6_typical_meteorological_year_direct_normal_irradiance.png){height=400px}
  <figcaption>TMY Direct Normal Irradiance showing selected representative months from the long-term dataset</figcaption>
</figure>

#### Global Horizontal Irradiance

<figure markdown="span">
  ![Typical Yearly Global Horizontal Irradiance](pvgis6_typical_meteorological_year_global_horizontal_irradiance.png){height=400px}
  <figcaption>TMY Global Horizontal Irradiance derived from SARAH-2 satellite data</figcaption>
</figure>

#### Temperature Variables

<figure markdown="span">
  ![Typical Minimum Dry Bulb Temperature](pvgis6_typical_meteorological_year_min_dry_bulb_temperature.png){height=400px}
  <figcaption>TMY Minimum Dry Bulb Temperature from ERA5 reanalysis data</figcaption>
</figure>

<figure markdown="span">
  ![Typical Yearly Mean Dry Bulb Temperature](pvgis6_typical_meteorological_year_mean_dry_bulb_temperature.png){height=400px}
  <figcaption>TMY Mean Dry Bulb Temperature at 2m height from ERA5</figcaption>
</figure>

<figure markdown="span">
  ![Typical Yearly Maximum Dry Bulb Temperature](pvgis6_typical_meteorological_year_max_dry_bulb_temperature.png){height=400px}
  <figcaption>TMY Maximum Dry Bulb Temperature showing peak daily values</figcaption>
</figure>

#### Humidity and Wind

<figure markdown="span">
  ![Typical Yearly Mean Relative Humidity](pvgis6_typical_meteorological_year_mean_relative_humidity.png){height=400px}
  <figcaption>TMY Mean Relative Humidity derived from ERA5 dewpoint and temperature data</figcaption>
</figure>

<figure markdown="span">
  ![Typical Yearly Wind Speed](pvgis6_typical_meteorological_year_mean_wind_speed.png){height=400px}
  <figcaption>TMY Mean Wind Speed at 10m height from ERA5 reanalysis</figcaption>
</figure>

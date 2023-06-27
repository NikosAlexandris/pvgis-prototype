# Photovoltaic Information System

## Demonstration

### CLI

``` bash                                                                                
 Usage: pvgis-prototype [OPTIONS] COMMAND [ARGS]...                             
                                                                                
 PVGIS core CLI prototype                                                       
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --verbose                 --no-verbose      [default: no-verbose]            │
│ --version             -v                    Show the application's version   │
│                                             and exit.                        │
│ --install-completion                        Install completion for the       │
│                                             current shell.                   │
│ --show-completion                           Show completion for the current  │
│                                             shell, to copy it or customize   │
│                                             the installation.                │
│ --help                                      Show this message and exit.      │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ manual      Manual for solar radiation variables                             │
│ geometry    Calculate solar geometry parameters for a location and moment in │
│             time                                                             │
│ time        Calculate the solar time for a location and moment in time       │
│ irradiance  Calculate solar irradiance                                       │
│ tmy         Generate a Typical Meteorological Year                           │
│ energy      Estimate the energy production of a PV system                    │
│ series      Retrieve time series of solar radiation and PV power output      │
│ helpers     Various diagnostic functions                                     │
╰──────────────────────────────────────────────────────────────────────────────╯
```

#### Solar time

Available parameters?

``` bash
 Usage: pvgis-prototype time [OPTIONS] LONGITUDE LATITUDE                       
                             [TIMESTAMP]:[%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d   
                             %H:%M:%S] COMMAND [ARGS]...                        
                                                                                
 Calculate the solar time for a location and moment in time                     
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    longitude      FLOAT RANGE                 [default: None] [required]   │
│ *    latitude       FLOAT RANGE                 [default: None] [required]   │
│      timestamp      [TIMESTAMP]:[%Y-%m-%d|%Y-%  Timestamp                    │
│                     m-%dT%H:%M:%S|%Y-%m-%d      [default: (dynamic)]         │
│                     %H:%M:%S]                                                │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --timezone                    TEXT                   Timezone                │
│                                                      [default: None]         │
│ --days-in-a-year              FLOAT                  Days in a year          │
│                                                      [default: 365.25]       │
│ --perigee-offset              FLOAT                  Perigee offset          │
│                                                      [default: 0.048869]     │
│ --eccentricity                FLOAT                  Eccentricity            │
│                                                      [default: 0.01672]      │
│ --time-offset-global          FLOAT                  Global time offset      │
│                                                      [default: 0]            │
│ --hour-offset                 FLOAT                  Hour offset             │
│                                                      [default: 0]            │
│ --model               -m      [eot|ephem|NOAA|pvgis  Model to calculate      │
│                               |Skyfield]             solar time              │
│                                                      [default:               │
│                                                      SolarTimeModels.ephem]  │
│ --help                                               Show this message and   │
│                                                      exit.                   │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Examples for `time`

Based on Skyfield

``` bash
pvgis-prototype time -m Skyfield 6.6327 46.5218 2023-06-26T12:04:25
```

``` bash
Solar time: 0.0183169325 (UTC)
```

Based on NOAA's equation of time

``` bash
pvgis-prototype time -m NOAA 6.6327 46.5218 2023-06-26T12:04:25
```

``` bash
Solar time: 0.041037615 (UTC)
```

### API 

First, run the server:

``` bash
uvicorn pvgisprototype.webapi:app --reload
```

Then, test some endpoints!

#### Solar time

- [`http://localhost:8000/calculate_solar_time_skyfield/?longitude=-70&latitude=40&timestamp=2023-06-26T12:00:00&timezone=America/New_York`](http://localhost:8000/calculate_solar_time_skyfield/?longitude=-70&latitude=40&timestamp=2023-06-26T12:00:00&timezone=America/New_York)

- [`http://localhost:8000/calculate_solar_time_skyfield/?longitude=6.6327&latitude=46.5218&timestamp=2023-06-26T12:04:25&timezone=CET`](http://localhost:8000/calculate_solar_time_skyfield/?longitude=6.6327&latitude=46.5218&timestamp=2023-06-26T12:04:25&timezone=CET)


#### Direct inclined irradiance

- API endpoint to calculate the direct inclined irradiance:

```
..
```

#### Plot solar declination

- [Plot solar declination for 2023](http://localhost:8000/plot_solar_declination_one_year_bokeh?year=2023)

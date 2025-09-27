#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
"""
>>> This file is not used at the moment. It is kept as a reference ! <<<

Variables weight for the FS statistics under each methodology

| Index of daily values         | ISO 15927-4_2005 | Sandia Method | NSRDB TMY |
|-------------------------------+------------------+---------------+-----------|
| Maximum Dry Bulb Temperature  | 0                | 1/24          | 1/20      |
| Minimum Dry Bulb Temperature  | 0                | 1/24          | 1/20      |
| Mean Dry Bulb Temperature     | 1                | 2/24          | 2/20      |
| Maximum Dew Point Temperature | 0                | 1/24          | 1/20      |
| Minimum Dew Point Temperature | 0                | 1/24          | 1/20      |
| Mean Dew Point Temperature    | 0                | 2/24          | 2/20      |
| Maximum Wind Velocity         | 0                | 2/24          | 1/20      |
| Mean Wind Velocity            | 0*               | 2/24          | 1/20      |
| Mean Relative Humidity        | 1                | 0             | 0         |
| Global horizontal irradiance  | 1                | 12/24         | 5/20      |
| Direct normal irradiance      | 0                | 0             | 5/20      |

iso_15927_4 = "ISO 15927-4_2005"
sandia = "Sandia Method"
nsrdb = "NSRDB TMY"
"""

iso_15927_4 = {
    "Maximum Dry Bulb Temperature": 0,
    "Minimum Dry Bulb Temperature": 0,
    "Mean Dry Bulb Temperature": 1,
    "Maximum Dew Point Temperature": 0,
    "Minimum Dew Point Temperature": 0,
    "Mean Dew Point Temperature": 0,
    "Maximum Wind Velocity": 0,
    "Mean Wind Velocity": 0,
    "Mean Relative Humidity": 1,
    "Global Horizontal Irradiance": 1,
    "Direct Normal Irradiance": 0,
}

sandia = {
    "Maximum Dry Bulb Temperature": 1/24,
    "Minimum Dry Bulb Temperature": 1/24,
    "Mean Dry Bulb Temperature": 2/24,
    "Maximum Dew Point Temperature": 1/24,
    "Minimum Dew Point Temperature": 1/24,
    "Mean Dew Point Temperature": 2/24,
    "Maximum Wind Velocity": 2/24,
    "Mean Wind Velocity": 2/24,
    "Mean Relative Humidity": 0,
    "Global Horizontal Irradiance": 12/24,
    "Direct Normal Irradiance": 0
}

nsrdb = {
    "Maximum Dry Bulb Temperature": 1/20,
    "Minimum Dry Bulb Temperature": 1/20,
    "Mean Dry Bulb Temperature": 2/20,
    "Maximum Dew Point Temperature": 1/20,
    "Minimum Dew Point Temperature": 1/20,
    "Mean Dew Point Temperature": 2/20,
    "Maximum Wind Velocity": 1/20,
    "Mean Wind Velocity": 1/20,
    "Mean Relative Humidity": 0,
    "Global Horizontal Irradiance": 5/20,
    "Direct Normal Irradiance": 5/20
}

weights_24_32 = {
    "Dry-bulb temperature (maximum)": 1/24,
    "Dry-bulb temperature (minimum)": 1/24,
    "Dry-bulb temperature (mean)": 2/24,
    "Dry-bulb temperature (range)": None,
    "Dew point temperature (maximum)": 1/24,
    "Dew point temperature (minimum)": 1/24,
    "Dew point temperature (mean)": 2/24,
    "Dew point temperature (range)": None,
    "Relative humidity (maximum)": None,
    "Relative humidity (minimum)": None,
    "Relative humidity (mean)": None,
    "Relative humidity (range)": None,
    "Wind speed (maximum)": 2/24,
    "Wind speed (minimum)": None,
    "Wind speed (mean)": 2/24,
    "Wind speed (range)": None,
    "Wind direction (mean)": None,
    "Global horizontal irradiance": 12/24,
    "Horizontal beam irradiance": None
}

weights_18 = {
    "Dry-bulb temperature (maximum)": 5/100,
    "Dry-bulb temperature (minimum)": 5/100,
    "Dry-bulb temperature (mean)": 30/100,
    "Dry-bulb temperature (range)": None,
    "Dew point temperature (maximum)": 2.5/100,
    "Dew point temperature (minimum)": 2.5/100,
    "Dew point temperature (mean)": 5/100,
    "Dew point temperature (range)": None,
    "Relative humidity (maximum)": None,
    "Relative humidity (minimum)": None,
    "Relative humidity (mean)": None,
    "Relative humidity (range)": None,
    "Wind speed (maximum)": 5/100,
    "Wind speed (minimum)": None,
    "Wind speed (mean)": 5/100,
    "Wind speed (range)": None,
    "Wind direction (mean)": None,
    "Global horizontal irradiance": 40/100,
    "Horizontal beam irradiance": None
}

weights_33 = {
    "Dry-bulb temperature (maximum)": 1/24,
    "Dry-bulb temperature (minimum)": 1/24,
    "Dry-bulb temperature (mean)": 1/24,
    "Dry-bulb temperature (range)": None,
    "Dew point temperature (maximum)": 1/24,
    "Dew point temperature (minimum)": 1/24,
    "Dew point temperature (mean)": 1/24,
    "Dew point temperature (range)": None,
    "Relative humidity (maximum)": None,
    "Relative humidity (minimum)": None,
    "Relative humidity (mean)": None,
    "Relative humidity (range)": None,
    "Wind speed (maximum)": 1/24,
    "Wind speed (minimum)": None,
    "Wind speed (mean)": 1/24,
    "Wind speed (range)": None,
    "Wind direction (mean)": None,
    "Global horizontal irradiance": 12/24,
    "Horizontal beam irradiance": 5/20
}

weights_16_17 = {
    "Dry-bulb temperature (maximum)": 1/20,
    "Dry-bulb temperature (minimum)": 1/20,
    "Dry-bulb temperature (mean)": 2/20,
    "Dry-bulb temperature (range)": 1/32,
    "Dew point temperature (maximum)": 1/20,
    "Dew point temperature (minimum)": 1/20,
    "Dew point temperature (mean)": 2/20,
    "Dew point temperature (range)": 1/32,
    "Relative humidity (maximum)": 1/32,
    "Relative humidity (minimum)": 1/32,
    "Relative humidity (mean)": 2/32,
    "Relative humidity (range)": 1/32,
    "Wind speed (maximum)": 1/20,
    "Wind speed (minimum)": 1/32,
    "Wind speed (mean)": 1/20,
    "Wind speed (range)": 1/32,
    "Wind direction (mean)": 1/32,
    "Global horizontal irradiance": 5/20,
    "Horizontal beam irradiance": 8/32
}

weights_34 = {
    "Dry-bulb temperature (maximum)": 1/10,
    "Dry-bulb temperature (minimum)": 1/10,
    "Dry-bulb temperature (mean)": 2/10,
    "Dry-bulb temperature (range)": 1/10,
    "Dew point temperature (maximum)": 1/10,
    "Dew point temperature (minimum)": 1/10,
    "Dew point temperature (mean)": 2/10,
    "Dew point temperature (range)": 1/10,
    "Relative humidity (maximum)": None,
    "Relative humidity (minimum)": None,
    "Relative humidity (mean)": None,
    "Relative humidity (range)": None,
    "Wind speed (maximum)": None,
    "Wind speed (minimum)": None,
    "Wind speed (mean)": None,
    "Wind speed (range)": None,
    "Wind direction (mean)": None,
    "Global horizontal irradiance": None,
    "Horizontal beam irradiance": 8/32
}

weights_35 = {
    "Dry-bulb temperature (maximum)": 1/32,
    "Dry-bulb temperature (minimum)": 1/32,
    "Dry-bulb temperature (mean)": 2/32,
    "Dry-bulb temperature (range)": 1/32,
    "Dew point temperature (maximum)": 1/32,
    "Dew point temperature (minimum)": 1/32,
    "Dew point temperature (mean)": 2/32,
    "Dew point temperature (range)": 1/32,
    "Relative humidity (maximum)": None,
    "Relative humidity (minimum)": None,
    "Relative humidity (mean)": None,
    "Relative humidity (range)": None,
    "Wind speed (maximum)": 1/32,
    "Wind speed (minimum)": 1/32,
    "Wind speed (mean)": 2/32,
    "Wind speed (range)": 1/32,
    "Wind direction (mean)": 1/32,
    "Global horizontal irradiance": 8/32,
    "Horizontal beam irradiance": 8/32
}

weights_36 = {
    "Dry-bulb temperature (maximum)": 1/24,
    "Dry-bulb temperature (minimum)": 1/24,
    "Dry-bulb temperature (mean)": 3/24,
    "Dry-bulb temperature (range)": None,
    "Dew point temperature (maximum)": None,
    "Dew point temperature (minimum)": None,
    "Dew point temperature (mean)": None,
    "Dew point temperature (range)": None,
    "Relative humidity (maximum)": None,
    "Relative humidity (minimum)": None,
    "Relative humidity (mean)": None,
    "Relative humidity (range)": None,
    "Wind speed (maximum)": 2/24,
    "Wind speed (minimum)": None,
    "Wind speed (mean)": 2/24,
    "Wind speed (range)": None,
    "Wind direction (mean)": None,
    "Global horizontal irradiance": 12/24,
    "Horizontal beam irradiance": None
}

weights_37e39 = {
    "Dry-bulb temperature (maximum)": 1/24,
    "Dry-bulb temperature (minimum)": 1/24,
    "Dry-bulb temperature (mean)": 2/24,
    "Dry-bulb temperature (range)": 1/22,
    "Dew point temperature (maximum)": None,
    "Dew point temperature (minimum)": None,
    "Dew point temperature (mean)": None,
    "Dew point temperature (range)": None,
    "Relative humidity (maximum)": 1/24,
    "Relative humidity (minimum)": 1/24,
    "Relative humidity (mean)": 2/24,
    "Relative humidity (range)": 1/22,
    "Wind speed (maximum)": 2/24,
    "Wind speed (minimum)": None,
    "Wind speed (mean)": 2/24,
    "Wind speed (range)": 1/22,
    "Wind direction (mean)": None,
    "Global horizontal irradiance": None,
    "Horizontal beam irradiance": None
}

weights_40 = {
    "Dry-bulb temperature (maximum)": 1/22,
    "Dry-bulb temperature (minimum)": 1/22,
    "Dry-bulb temperature (mean)": 1/22,
    "Dry-bulb temperature (range)": 1/22,
    "Dew point temperature (maximum)": None,
    "Dew point temperature (minimum)": None,
    "Dew point temperature (mean)": None,
    "Dew point temperature (range)": None,
    "Relative humidity (maximum)": None,
    "Relative humidity (minimum)": None,
    "Relative humidity (mean)": None,
    "Relative humidity (range)": None,
    "Wind speed (maximum)": 1/22,
    "Wind speed (minimum)": None,
    "Wind speed (mean)": 1/22,
    "Wind speed (range)": 1/22,
    "Wind direction (mean)": None,
    "Global horizontal irradiance": 11/22,
    "Horizontal beam irradiance": 12/24
}

weights_41 = {
    "Dry-bulb temperature (maximum)": 1/20,
    "Dry-bulb temperature (minimum)": 1/20,
    "Dry-bulb temperature (mean)": 3/20,
    "Dry-bulb temperature (range)": None,
    "Dew point temperature (maximum)": None,
    "Dew point temperature (minimum)": None,
    "Dew point temperature (mean)": None,
    "Dew point temperature (range)": None,
    "Relative humidity (maximum)": None,
    "Relative humidity (minimum)": 1/20,
    "Relative humidity (mean)": 2/20,
    "Relative humidity (range)": None,
    "Wind speed (maximum)": 1/20,
    "Wind speed (minimum)": None,
    "Wind speed (mean)": 1/20,
    "Wind speed (range)": None,
    "Wind direction (mean)": None,
    "Global horizontal irradiance": 5/20,
    "Horizontal beam irradiance": 5/20,
    "Other": None
}

weights_42 = {
    "Dry-bulb temperature (maximum)": 1/24,
    "Dry-bulb temperature (minimum)": None,
    "Dry-bulb temperature (mean)": None,
    "Dry-bulb temperature (range)": None,
    "Dew point temperature (maximum)": None,
    "Dew point temperature (minimum)": None,
    "Dew point temperature (mean)": None,
    "Dew point temperature (range)": None,
    "Relative humidity (maximum)": 1/24,
    "Relative humidity (minimum)": None,
    "Relative humidity (mean)": None,
    "Relative humidity (range)": None,
    "Wind speed (maximum)": 11/24,
    "Wind speed (minimum)": None,
    "Wind speed (mean)": None,
    "Wind speed (range)": None,
    "Wind direction (mean)": None,
    "Global horizontal irradiance": 11/24,
    "Horizontal beam irradiance": None,
    "Other": None
}

weights_43 = {
    "Dry-bulb temperature (maximum)": 1/20,
    "Dry-bulb temperature (minimum)": 1/20,
    "Dry-bulb temperature (mean)": 6/20,
    "Dry-bulb temperature (range)": None,
    "Dew point temperature (maximum)": None,
    "Dew point temperature (minimum)": None,
    "Dew point temperature (mean)": 4/24,
    "Dew point temperature (range)": None,
    "Relative humidity (maximum)": 1/40,
    "Relative humidity (minimum)": 1/40,
    "Relative humidity (mean)": 1/20,
    "Relative humidity (range)": None,
    "Wind speed (maximum)": 1/20,
    "Wind speed (minimum)": None,
    "Wind speed (mean)": 1/20,
    "Wind speed (range)": None,
    "Wind direction (mean)": None,
    "Global horizontal irradiance": 8/20,
    "Horizontal beam irradiance": None,
    "Other": None
}

weights_44_45 = {
    "Dry-bulb temperature (maximum)": 1/24,
    "Dry-bulb temperature (minimum)": 1/24,
    "Dry-bulb temperature (mean)": 2/24,
    "Dry-bulb temperature (range)": 1/24,
    "Dew point temperature (maximum)": None,
    "Dew point temperature (minimum)": None,
    "Dew point temperature (mean)": None,
    "Dew point temperature (range)": None,
    "Relative humidity (maximum)": None,
    "Relative humidity (minimum)": None,
    "Relative humidity (mean)": None,
    "Relative humidity (range)": None,
    "Wind speed (maximum)": 2/24,
    "Wind speed (minimum)": None,
    "Wind speed (mean)": 2/24,
    "Wind speed (range)": None,
    "Wind direction (mean)": None,
    "Global horizontal irradiance": 12/24,
    "Horizontal beam irradiance": None
}

weights_46 = {
    "Dry-bulb temperature (maximum)": 1/100,
    "Dry-bulb temperature (minimum)": 2/100,
    "Dry-bulb temperature (mean)": 1/100,
    "Dry-bulb temperature (range)": None,
    "Dew point temperature (maximum)": 2/100,
    "Dew point temperature (minimum)": None,
    "Dew point temperature (mean)": 1/100,
    "Dew point temperature (range)": None,
    "Relative humidity (maximum)": None,
    "Relative humidity (minimum)": None,
    "Relative humidity (mean)": None,
    "Relative humidity (range)": None,
    "Wind speed (maximum)": 4/100,
    "Wind speed (minimum)": None,
    "Wind speed (mean)": 2/100,
    "Wind speed (range)": None,
    "Wind direction (mean)": 1/100,
    "Global horizontal irradiance": None,
    "Horizontal beam irradiance": 85/100
}

weights_47 = {
    "Dry-bulb temperature (maximum)": 1/24,
    "Dry-bulb temperature (minimum)": 1/24,
    "Dry-bulb temperature (mean)": 3/24,
    "Dry-bulb temperature (range)": None,
    "Dew point temperature (maximum)": None,
    "Dew point temperature (minimum)": None,
    "Dew point temperature (mean)": None,
    "Dew point temperature (range)": None,
    "Relative humidity (maximum)": None,
    "Relative humidity (minimum)": 1/24,
    "Relative humidity (mean)": 2/24,
    "Relative humidity (range)": None,
    "Wind speed (maximum)": 2/24,
    "Wind speed (minimum)": None,
    "Wind speed (mean)": 2/24,
    "Wind speed (range)": None,
    "Wind direction (mean)": None,
    "Global horizontal irradiance": 12/24,
    "Horizontal beam irradiance": 8/32
}

weights_48 = {
    "Dry-bulb temperature (maximum)": 2/16,
    "Dry-bulb temperature (minimum)": 1/16,
    "Dry-bulb temperature (mean)": 1/16,
    "Dry-bulb temperature (range)": 1/32,
    "Dew point temperature (maximum)": None,
    "Dew point temperature (minimum)": None,
    "Dew point temperature (mean)": None,
    "Dew point temperature (range)": None,
    "Relative humidity (maximum)": None,
    "Relative humidity (minimum)": None,
    "Relative humidity (mean)": None,
    "Relative humidity (range)": 1/32,
    "Wind speed (maximum)": None,
    "Wind speed (minimum)": None,
    "Wind speed (mean)": 1/16,
    "Wind speed (range)": 1/32,
    "Wind direction (mean)": None,
    "Global horizontal irradiance": 8/16,
    "Horizontal beam irradiance": None
}

weights_49 = {
    "Dry-bulb temperature (maximum)": 1/32,
    "Dry-bulb temperature (minimum)": 1/32,
    "Dry-bulb temperature (mean)": 2/32,
    "Dry-bulb temperature (range)": 1/32,
    "Dew point temperature (maximum)": None,
    "Dew point temperature (minimum)": None,
    "Dew point temperature (mean)": None,
    "Dew point temperature (range)": None,
    "Relative humidity (maximum)": 1/32,
    "Relative humidity (minimum)": 1/32,
    "Relative humidity (mean)": 2/32,
    "Relative humidity (range)": 1/32,
    "Wind speed (maximum)": 1/32,
    "Wind speed (minimum)": 1/32,
    "Wind speed (mean)": 2/32,
    "Wind speed (range)": 1/32,
    "Wind direction (mean)": 1/32,
    "Global horizontal irradiance": 8/32,
    "Horizontal beam irradiance": 8/32
}

weights_50 = {
    "Dry-bulb temperature (maximum)": 5/100,
    "Dry-bulb temperature (minimum)": 5/100,
    "Dry-bulb temperature (mean)": 30/100,
    "Dry-bulb temperature (range)": None,
    "Dew point temperature (maximum)": None,
    "Dew point temperature (minimum)": None,
    "Dew point temperature (mean)": None,
    "Dew point temperature (range)": None,
    "Relative humidity (maximum)": None,
    "Relative humidity (minimum)": None,
    "Relative humidity (mean)": 10/100,
    "Relative humidity (range)": None,
    "Wind speed (maximum)": 5/100,
    "Wind speed (minimum)": None,
    "Wind speed (mean)": 5/100,
    "Wind speed (range)": None,
    "Wind direction (mean)": None,
    "Global horizontal irradiance": 40/100,
    "Horizontal beam irradiance": None
}

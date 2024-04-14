# Variables weight for the FS statistics under each methodology

# | Index of daily values         | ISO 15927-4_2005 | Sandia Method | NSRDB TMY |
# |-------------------------------+------------------+---------------+-----------|
# | Maximum Dry Bulb Temperature  | 0                | 1/24          | 1/20      |
# | Minimum Dry Bulb Temperature  | 0                | 1/24          | 1/20      |
# | Mean Dry Bulb Temperature     | 1                | 2/24          | 2/20      |
# | Maximum Dew Point Temperature | 0                | 1/24          | 1/20      |
# | Minimum Dew Point Temperature | 0                | 1/24          | 1/20      |
# | Mean Dew Point Temperature    | 0                | 2/24          | 2/20      |
# | Maximum Wind Velocity         | 0                | 2/24          | 1/20      |
# | Mean Wind Velocity            | 0*               | 2/24          | 1/20      |
# | Mean Relative Humidity        | 1                | 0             | 0         |
# | Global horizontal irradiance  | 1                | 12/24         | 5/20      |
# | Direct normal irradiance      | 0                | 0             | 5/20      |

weights = {
    "ISO 15927-4_2005": {
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
        "Direct Normal Irradiance": 0
    },
    "Sandia Method": {
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
    },
    "NSRDB TMY": {
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
}

# # Example usage: Accessing weights
# iso_weights = weights["ISO 15927-4_2005"]["Mean Dry Bulb Temperature"]
# sandia_ghi = weights["Sandia Method"]["Global Horizontal Irradiance"]
# nsrdb_wind = weights["NSRDB TMY"]["Mean Wind Velocity"]

# print(f"ISO Mean Dry Bulb Temperature Weight: {iso_weights}")
# print(f"Sandia Global Horizontal Irradiance Weight: {sandia_ghi}")
# print(f"NSRDB Mean Wind Velocity Weight: {nsrdb_wind}")

import pathlib
import netCDF4 as nc
import numpy as np
import pytest
from datetime import datetime, timedelta


# (longitude, latitude)
EU_GEOMETRIC_CENTER_POST_BREXIT = (9.902056, 49.843)
@pytest.fixture
def path_to_data():
    return pathlib.Path('data')


@pytest.fixture
def create_minimal_netcdf(path_to_data):
    
    np.random.seed(43)  # Fix the random seed to ensure reproducibility

    # Define the dimensions
    time = 24  # 24 hours
    lon = 1
    lat = 1

    # Create the netCDF file
    filename = path_to_data / "minimal_netcdf.nc"
    dataset = nc.Dataset(filename, "w", format="NETCDF4")

    # Create the dimensions
    dataset.createDimension("time", time)
    dataset.createDimension("lon", lon)
    dataset.createDimension("lat", lat)

    # Create the time variable
    time_var = dataset.createVariable("time", np.float64, ("time",))
    time_var.units = "hours since 1970-01-01 00:00:00"
    time_var.calendar = "standard"
    start_time = datetime(2023, 5, 23, 0, 0, 0)
    time_values = [start_time + timedelta(hours=h) for h in range(time)]
    time_var[:] = nc.date2num(time_values, units=time_var.units, calendar=time_var.calendar)

    # Create the longitude and latitude variables
    lon_var = dataset.createVariable("lon", np.float32, ("lon",))
    lon_var.units = "degrees_east"
    lon_var[:] = [EU_GEOMETRIC_CENTER_POST_BREXIT[0]]  # Set the longitude value

    lat_var = dataset.createVariable("lat", np.float32, ("lat",))
    lat_var.units = "degrees_north"
    lat_var[:] = [EU_GEOMETRIC_CENTER_POST_BREXIT[1]]  # Set the latitude value

    # Create the temperature variable
    temp_var = dataset.createVariable("t2m", np.float32, ("time", "lat", "lon"))
    temp_var.units = "K"
    # temp_data = np.random.uniform(low=280.0, high=310.0, size=(time, lat, lon))  # Generate random temperature values
    temp_data = np.random.uniform(low=280.0, high=310.0, size=(time, lat, lon))  # Generate random temperature values
    temp_var[:] = temp_data

    # Close the netCDF file
    dataset.close()

    return filename

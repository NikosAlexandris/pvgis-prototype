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
import sys

import xarray as xr

# from pvgisprototype.api.series.csv import to_csv


def main():
    time_series_1 = sys.argv[1]
    time_series_2 = sys.argv[2]
    longitude = float(sys.argv[3])
    latitude = float(sys.argv[4])
    data_1 = xr.open_dataset(time_series_1).sel(
        lon=longitude, lat=latitude, method="nearest"
    )
    data_2 = xr.open_dataset(time_series_2).sel(
        lon=longitude, lat=latitude, method="nearest"
    )
    data_1.to_dataframe().to_csv("series_1.csv")
    data_2.to_dataframe().to_csv("series_2.csv")
    # to_csv( x=selected_data, path=str(tocsv))
    # print('CSV file has been successfully created.')


if __name__ == "__main__":
    main()

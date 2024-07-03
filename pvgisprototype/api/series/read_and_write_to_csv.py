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

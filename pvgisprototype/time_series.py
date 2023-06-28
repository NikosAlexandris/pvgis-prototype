import typer
import xarray as xr


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help='Retrieve time series of solar radiation and PV power output',
)


def read_raster_data(netcdf: str, mask_and_scale=False):
    """
    """
    try:
        # logger.debug("%s", netcdf.name)
        dataarray = xr.open_dataarray(
                filename_or_obj=netcdf,
                mask_and_scale=mask_and_scale,
                )
        return dataarray

    except Exception as exc:
        # typer.echo(f"Couldn't open {dataset_type.value} dataset: {str(exc)}")
        typer.echo(f"Couldn't open dataset: {str(exc)}")
        raise typer.Exit(code=33)


@app.command()
def query_location(
        netcdf: str,
        longitude: float,
        latitude: float,
        mask_and_scale=False,
        method='nearest',
        ) -> int:
    """
    Query the value or time series over a specific location - Example command!
    """
    try:
        dataarray = read_raster_data(netcdf, mask_and_scale=mask_and_scale)
        data = dataarray.sel(
                lon=longitude,
                lat=latitude,
                method='nearest',
                )
        output = data.values.tolist()
        typer.echo(output)
        return 0

    except Exception as exc:
        typer.echo(f"Error: {str(exc)}")
        return 1


@app.command()
def hourly():
    """
    Time series of hourly solar radiation and PV power values

    The solar radiation data used by PVGIS consists of values for every hour over a period of several years, based on data from satellites and reanalysis. This part of PVGIS makes it possible to download the full set of hourly data for solar radiation and/or PV output power for the chosen location. Unlike the other parts of PVGIS, the data will not be shown as graphs but will be available for download only.

    """
    pass


@app.command()
def daily():
    """
    Daily solar radiation data profile
    
    In this section of PVGIS we show the average solar irradiation for each hour during the day for a chosen month, with the average taken over all days in that month during the multi-year time period for which we have data. In addition to calculating the average of the solar radiation the daily radiation application also calculates the daily variation in the clear-sky radiation, both for fixed and for 2-axis sun-tracking surfaces.
    """
    pass


@app.command()
def monthly():
    """
    Monthly solar radiation data
    
    Here we calculate the monthly averages of solar radiation for the chosen location, showing in graphs or tables how the average solar irradiation varies over a multi-year period. The results are given for radiation on horizontal and/or inclined planes, as well as Direct Normal Irradiation (DNI).
    """
    pass

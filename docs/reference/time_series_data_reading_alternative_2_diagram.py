from base64 import b64encode
from contextlib import suppress

from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom


icons_path = "docs/icons"

pvgis6_icon = "docs/logos/pvgis6_70px.png"
transmission_control_protocol_icon = f"{icons_path}/noun-transmission-control-protocol-6111114.svg"
data_analysis_icon = f"{icons_path}/noun-data-analysis.svg"
irradiance_icon = f"{icons_path}/wiggly_vertical_line.svg"
global_horizontal_irradiance_icon = f"{icons_path}/noun_global_horizontal_irradiance.svg"
direct_horizontal_irradiance_icon = f"{icons_path}/noun_direct_horizontal_irradiance.svg"
spectral_effect_icon = f"{icons_path}/noun-sun-525998_modified.svg"
temperature_icon = f"{icons_path}/thermometer.svg"
photovoltaic_power_icon = f"{icons_path}/noun-solar-energy-853048.svg"
wind_speed_icon = f"{icons_path}/noun-windsock-4502486.svg"  #Windsock by Dani Pomal from <a href="https://thenounproject.com/browse/icons/term/windsock/" target="_blank" title="Windsock Icons">Noun Project</a> (CC BY 3.0) 

data_array_icon = "docs/logos/data_array.svg"
# netcdf_icon = "docs/logos/netcdf-400x400.png"
netcdf_icon = "docs/overrides/.icons/custom/series_chunked.svg"
netcdf_continuous_in_time_icon = "docs/overrides/.icons/custom/series_continuous_in_time.svg"

kerchunk_icon = "docs/logos/kerchunk.png"
binary_data_icon = "docs/logos/pastebin.svg"
json_icon = "docs/logos/json.svg"
parquet_icon = "docs/logos/apacheparquet.svg"
zarr_icon = "docs/logos/zarr.png"  # zarr_logo_x.png
xarray_icon = "docs/logos/Xarray_RGB.svg"

pydantic_icon = "docs/logos/pydantic.png"

pandas_icon = "docs/logos/pandas.svg"
numpy_icon = "docs/logos/numpy.svg"
dask_icon = "docs/logos/dask.svg"
cupy_icon = "docs/logos/CuPy_300x300.png"

files_icon = f"{icons_path}/files.svg"

python = "docs/logos/python.svg"
c_icon = "docs/logos/c.svg"
cplusplus_icon = "docs/logos/cplusplus.svg"


try:
    with suppress(FileNotFoundError):
        graph_attr = {"splines":"spline", "fontsize": "25"}
        with Diagram("Reading Time Series", direction="LR", show=False, graph_attr=graph_attr) as diagram:
            diagram.render = lambda: None

            # Data

            NetCDF1 = Custom("1", netcdf_icon)
            NetCDF2 = Custom("2", netcdf_icon)
            NetCDFx = Custom("..x", netcdf_icon)

            # Input Data to PVGIS
            Zarr = Custom("Store", zarr_icon)

            # Tools
            Xarray = Custom("", xarray_icon)

            # Analysis of Photovoltaic Performance
            PVGIS_6 = Custom("PVGIS 6", pvgis6_icon)

            # Workflow =======================================================

            NetCDF1 - Edge(label='Rechunk continuous in time', style="dashed") >> Zarr
            NetCDF2 - Edge(label='Rechunk .. in time', style="dashed") >> Zarr
            NetCDFx - Edge(label='Rechunk .. in time', style="dashed") >> Zarr

            Zarr \
            - Edge(label="Read with Zarr engine", color="firebrick", style="dashed") \
            - Xarray \
            - Edge(label="", color="firebrick") \
            >> PVGIS_6

            # Encode diagram as a PNG and print it in HTML Image format

            png = b64encode(diagram.dot.pipe(format="png")).decode()

    # Finally, print the "flow"

    print(f'<img src="data:image/png;base64, {png}"/>')

except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()  # This prints the full traceback

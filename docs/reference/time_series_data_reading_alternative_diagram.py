from base64 import b64encode
from contextlib import suppress

from diagrams import Diagram, Edge
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
netcdf_icon = "docs/logos/netcdf-400x400.png"
netcdf_chunked_series_icon = "docs/overrides/.icons/custom/series_chunked.svg"
netcdf_continuous_in_time_icon = "docs/overrides/.icons/custom/series_continuous_in_time.svg"

mapserver_icon = "docs/logos/mapserver.svg"
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
        graph_attr = {"splines":"spline"}
        with Diagram("Reading Time Series - Alternative Workflow", direction="LR", show=False, graph_attr=graph_attr) as diagram:
            diagram.render = lambda: None

            # Data

            NetCDF1 = Custom("1", netcdf_chunked_series_icon)
            NetCDF2 = Custom("2", netcdf_chunked_series_icon)
            NetCDFx = Custom("..x", netcdf_chunked_series_icon)

            NetCDF1_Rechunked = Custom("1", netcdf_continuous_in_time_icon)
            NetCDF2_Rechunked = Custom("2", netcdf_continuous_in_time_icon)
            NetCDFx_Rechunked = Custom("..x", netcdf_continuous_in_time_icon)

            NetCDF_Large_Time_Series1 = Custom("Large Time Series a", netcdf_icon)
            NetCDF_Large_Time_Series2 = Custom("Large Time Series b", netcdf_icon)
            NetCDF_Large_Time_Seriesx = Custom("Large Time Series c", netcdf_icon)

            MapServer_tileindex = Custom("MapServer tileindex", mapserver_icon)
            VRT = Custom("GDAL VRT", '')

            # Tools

            rioXarray = Custom("rioxarray", '')

            # Input Data to PVGIS
            
            # Analysis of Photovoltaic Performance

            PVGIS_6 = Custom("PVGIS 6", pvgis6_icon)


            # Workflow =======================================================

            NetCDF1 - Edge(label='Rechunk', style="dashed") >> NetCDF1_Rechunked
            NetCDF2 - Edge(label='Rechunk', style="dashed") >> NetCDF2_Rechunked
            NetCDFx - Edge(label='Rechunk', style="dashed") >> NetCDFx_Rechunked

            Empty2 = Custom("", '')
            Emptyx = Custom("", '')
            Empty2 - Edge(style="dashed") - NetCDF_Large_Time_Series2
            Emptyx - Edge(style="dashed") - NetCDF_Large_Time_Seriesx

            [NetCDF_Large_Time_Series1, NetCDF_Large_Time_Series2, NetCDF_Large_Time_Seriesx] \
            - Edge(label='Create tileindex record',  style='dashed') \
            - MapServer_tileindex \
            - Edge(label='Build VRT',  style='dashed') \
            >> VRT


            [NetCDF1_Rechunked, NetCDF2_Rechunked, NetCDFx_Rechunked] \
            - Edge(label="Read", color="firebrick", style="dashed") \
            - NetCDF_Large_Time_Series1

            VRT \
            - rioXarray \
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

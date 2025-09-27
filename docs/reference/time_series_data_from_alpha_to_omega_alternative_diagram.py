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
cupy_icon = "docs/logos/CuPy_300x300.png"
xarray_icon = "docs/logos/Xarray_RGB.svg"
# netcdf_icon = "docs/logos/netcdf-400x400.png"
netcdf_icon = "docs/overrides/.icons/custom/series_chunked.svg"
netcdf_continuous_in_time_icon = "docs/overrides/.icons/custom/series_continuous_in_time.svg"
data_array_icon = "docs/logos/data_array.svg"
numpy_icon = "docs/logos/numpy.svg"
dask_icon = "docs/logos/dask.svg"
pydantic_icon = "docs/logos/pydantic.png"
zarr_icon = "docs/logos/zarr.png"  # zarr_logo_x.png
kerchunk_icon = "docs/logos/kerchunk.png"
binary_data_icon = "docs/logos/pastebin.svg"
json_icon = "docs/logos/json.svg"
parquet_icon = "docs/logos/apacheparquet.svg"
files_icon = f"{icons_path}/files.svg"
pandas_icon = "docs/logos/pandas.svg"
python = "docs/logos/python.svg"
c_icon = "docs/logos/c.svg"
cplusplus_icon = "docs/logos/cplusplus.svg"


try:
    with suppress(FileNotFoundError):
        graph_attr = {"splines":"spline"}
        with Diagram("Analysis of Photovoltaic Performance", direction="LR", show=False, graph_attr=graph_attr) as diagram:
            diagram.render = lambda: None


            # "Raw" Data Acquisition & Production

            Satellite_to_Data = Custom("Data Acquisition", transmission_control_protocol_icon)
            ERA5_Data = Custom("ERA5 Reanalysis Data", data_array_icon)
            Analysis = Custom("Analysis & Production", data_analysis_icon)


            # Data

            #Data = Custom("Data / Observations", files_icon)
            #Files = Custom("Files", files_icon)

            NetCDF = Custom("Chunked data\nin NetCDF format", netcdf_icon)
            #with Cluster("Original product"):
            #    NetCDF1 = Custom("1", netcdf_icon)
            #    NetCDF2 = Custom("2", netcdf_icon)
            #    NetCDFx = Custom("..x", netcdf_icon)

            NetCDF1 = Custom("1", netcdf_icon)
            NetCDF2 = Custom("2", netcdf_icon)
            NetCDFx = Custom("..x", netcdf_icon)

            # Rechunk_NetCDF = Action(
            #     "Rechunk to contiguous in time",
            #     xlabel="nccopy",
            # )

            # NetCDF_Rechunked = Custom("1, 2, .. x\nContiguous in time", netcdf_icon)
            #with Cluster("Contiguous in time"):
            #    NetCDF1_Rechunked = Custom("1", netcdf_icon)
            #    NetCDF2_Rechunked = Custom("2", netcdf_icon)
            #    NetCDFx_Rechunked = Custom("..x", netcdf_icon)

            NetCDF1_Rechunked = Custom("1", netcdf_continuous_in_time_icon)
            NetCDF2_Rechunked = Custom("2", netcdf_continuous_in_time_icon)
            NetCDFx_Rechunked = Custom("..x", netcdf_continuous_in_time_icon)


            with Cluster("Time Series"):

                with Cluster("SARAH 2/3 climate records"):
                    Global_Horizontal_Irradiance = Custom("Global Horizontal Irradiance\n(GHI)", global_horizontal_irradiance_icon)
                    Direct_Horizontal_Irradiance = Custom("Direct Horizontal Irradiance\n(DHI)", direct_horizontal_irradiance_icon)
            
                with Cluster("ERA5 Reanalysis Data"):
                    Temperature = Custom("Temperature", temperature_icon)
                    Wind_Speed = Custom("Wind Speed", wind_speed_icon)

                Spectral_Effect = Custom("\nSpectral Factor", spectral_effect_icon)


            # Tools

            # Kerchunk

            Kerchunk = Custom("Kerchunk", kerchunk_icon)
            #In_Memory = Custom("First Call Read In Memory", '')
            Xarray = Custom("", xarray_icon)


            # Pre-Processed Data

            with Cluster('*First Call Read In-Memory'):
                Index = Custom("Index", binary_data_icon)
                with Cluster("Optional Formats"):
                    JSON = Custom("JSON (Slow!)", json_icon)
                    Parquet = Custom("Parquet (Fast)", parquet_icon)


            # Input Data to PVGIS
            
            with Cluster("Time Series for Photovoltaic Analysis"):

                Virtual_Zarr = Custom("Virtual Zarr store", zarr_icon)


            # Analysis of Photovoltaic Performance

            with Cluster("Photovoltaic Performance Analysis"):
                PVGIS_6 = Custom("PVGIS 6", pvgis6_icon)


            Photovoltaic_Power = Custom("Photovoltaic Energy\nPVGIS 6", photovoltaic_power_icon)


            # Workflow =======================================================

            # Format of Time Series Data

            Satellite_to_Data >> Global_Horizontal_Irradiance >> NetCDF
            Satellite_to_Data >> Direct_Horizontal_Irradiance >> NetCDF

            Satellite_to_Data \
            - Edge(label="+", style="dashed") \
            - Analysis \
            >> ERA5_Data

            ERA5_Data >> Temperature >> NetCDF
            ERA5_Data >> Wind_Speed >> NetCDF
            Analysis >> Spectral_Effect >> NetCDF


            # PVGIS 6

            Index - Edge(style="dashed") - Parquet
            Index - Edge(style="dashed") - JSON


            NetCDF >> [NetCDF1, NetCDF2, NetCDFx]

            NetCDF1 - Edge(label='Rechunk\ncontinuous in time', style="dashed") >> NetCDF1_Rechunked
            NetCDF2 - Edge(label='Rechunk .. in time', style="dashed") >> NetCDF2_Rechunked
            NetCDFx - Edge(label='Rechunk .. in time', style="dashed") >> NetCDFx_Rechunked

            [NetCDF1_Rechunked, NetCDF2_Rechunked, NetCDFx_Rechunked] \
            - Edge(label="Scan", color="firebrick", style="dashed") \
            - Kerchunk \
            - Edge(
                   label="Generate Index /\nVirtual Zarr",
                   color="firebrick",
                   style="dashed"
                  ) \
            - Index \
            - Edge(label="", color="firebrick", style="dashed") \
            - Virtual_Zarr \
            - Edge(label="Read with Zarr engine", color="firebrick", style="dashed") \
            - Xarray \
            - Edge(label="", color="firebrick") \
            - PVGIS_6 \
            >> Photovoltaic_Power


            # Encode diagram as a PNG and print it in HTML Image format

            png = b64encode(diagram.dot.pipe(format="png")).decode()

    # Finally, print the "flow"

    print(f'<img src="data:image/png;base64, {png}"/>')

except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()  # This prints the full traceback

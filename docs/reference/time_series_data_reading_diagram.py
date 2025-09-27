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

data_array_icon = "docs/logos/data_array.svg"
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
        graph_attr = {"splines":"spline"}
        with Diagram("Reading Time Series", direction="LR", show=False, graph_attr=graph_attr) as diagram:
            diagram.render = lambda: None

            # Data

            NetCDF1_Rechunked = Custom("Continuous in time 1", netcdf_continuous_in_time_icon)
            NetCDF2_Rechunked = Custom(".. 2", netcdf_continuous_in_time_icon)
            NetCDFx_Rechunked = Custom(".. x", netcdf_continuous_in_time_icon)

            # Tools

            #In_Memory = Custom("First Call Read In Memory", '')
            Xarray = Custom("", xarray_icon)


            # Pre-Processed Data

            with Cluster('*First Call Read In-Memory'):
                Index = Custom("Index", binary_data_icon)
                with Cluster("Optional Formats"):
                    JSON = Custom("JSON (Slow!)", json_icon)
                    Parquet = Custom("Parquet (Fast)", parquet_icon)


            # Input Data to PVGIS
            
            Virtual_Zarr = Custom("", zarr_icon)

            # Analysis of Photovoltaic Performance

            PVGIS_6 = Custom("PVGIS 6", pvgis6_icon)


            # Workflow =======================================================

            Index - Edge(style="dashed") - Parquet
            Index - Edge(style="dashed") - JSON

            [NetCDF1_Rechunked, NetCDF2_Rechunked, NetCDFx_Rechunked] \
            - Edge(label="Read", color="firebrick", style="dashed") \
            - Index \
            - Edge(label="", color="firebrick", style="dashed") \
            - Virtual_Zarr \
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

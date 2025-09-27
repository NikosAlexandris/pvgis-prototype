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
netcdf_icon = "docs/logos/netcdf-400x400.png"
# data_array_icon = "docs/logos/data_array.svg"
data_array_icon = "docs/logos/data_array.svg"
numpy_icon = "docs/logos/numpy.svg"
dask_icon = "docs/logos/dask.svg"
pydantic_icon = "docs/logos/pydantic.png"
zarr_icon = "docs/logos/zarr.png"  # zarr_logo_x.png
kerchunk_icon = "docs/logos/kerchunk.png"
binary_data_icon = "docs/logos/pastebin.svg"
files_icon = f"{icons_path}/files.svg"
pandas_icon = "docs/logos/pandas.svg"
python = "docs/logos/python.svg"
c_icon = "docs/logos/c.svg"
cplusplus_icon = "docs/logos/cplusplus.svg"


try:
    with suppress(FileNotFoundError):
        with Diagram("Time Series Data for Photovoltaic Performance Analysis", direction="TB", show=False) as diagram:
            diagram.render = lambda: None


            # "Raw" Data Acquisition & Production

            Satellite_to_Data = Custom("Data Acquisition", transmission_control_protocol_icon)
            ERA5_Data = Custom("ERA5 Reanalysis Data", data_array_icon)
            Analysis = Custom("Analysis & Production", data_analysis_icon)


            # Data

            Data = Custom("Data / Observations", files_icon)
            Files = Custom("Data", files_icon)
            NetCDF = Custom("1, 2, .. x", netcdf_icon)


            with Cluster("Time Series"):

                with Cluster("SARAH 2/3 climate records"):
                    Global_Horizontal_Irradiance = Custom("Global Horizontal Irradiance\n(GHI)", global_horizontal_irradiance_icon)
                    Direct_Horizontal_Irradiance = Custom("Direct Horizontal Irradiance\n(DHI)", direct_horizontal_irradiance_icon)
            
                with Cluster("ERA5 Reanalysis Data"):
                    Temperature = Custom("Temperature", temperature_icon)
                    Wind_Speed = Custom("Wind Speed", wind_speed_icon)

                Spectral_Effect = Custom("\nSpectral Factor", spectral_effect_icon)



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

            # Encode diagram as a PNG and print it in HTML Image format

            png = b64encode(diagram.dot.pipe(format="png")).decode()

    # Finally, print the "flow"

    print(f'<img src="data:image/png;base64, {png}"/>')


except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()  # This prints the full traceback

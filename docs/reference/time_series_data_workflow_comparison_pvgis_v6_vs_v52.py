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
from diagrams.programming.language import C
from diagrams.programming.language import Cpp


pvgis6_icon = "docs/logos/pvgis6_70px.png"
irradiance_icon = "docs/icons/wiggly_vertical_line.svg"
spectral_effect_icon = "docs/icons/noun-sun-525998.svg"
temperature_icon = "docs/icons/thermometer.svg"
photovoltaic_power_icon = "docs/icons/noun-solar-energy-853048.svg"
wind_speed_icon = "docs/icons/noun-windsock-4502486.svg"  #Windsock by Dani Pomal from <a href="https://thenounproject.com/browse/icons/term/windsock/" target="_blank" title="Windsock Icons">Noun Project</a> (CC BY 3.0) 
cupy_icon = "docs/logos/CuPy_300x300.png"
xarray_icon = "docs/logos/Xarray_RGB.svg"
netcdf_icon = "docs/logos/netcdf-400x400.png"
numpy_icon = "docs/logos/numpy.svg"
dask_icon = "docs/logos/dask.svg"
pydantic_icon = "docs/logos/pydantic.png"
zarr_icon = "docs/logos/zarr.png"  # zarr_logo_x.png
kerchunk_icon = "docs/logos/kerchunk.png"
binary_data_icon = "docs/logos/pastebin.svg"
files_icon = "docs/icons/files.svg"
pandas_icon = "docs/logos/pandas.svg"
python = "docs/logos/python.svg"
c_icon = "docs/logos/c.svg"
cplusplus_icon = "docs/logos/cplusplus.svg"


try:
    with suppress(FileNotFoundError):
        with Diagram("Analysis of Photovoltaic Performance", direction="TB", show=False) as diagram:
            diagram.render = lambda: None

            # PVGIS software version 5/6

            with Cluster("PVGIS <= 5.x"):
                PVGIS_5 = C("")
                PVGIS_5Cpp = Cpp("")

            with Cluster("PVGIS 6"):
                PVGIS_6 = Custom("PVGIS 6", pvgis6_icon)
                NumPy = Custom("NumPy", numpy_icon)
                Xarray = Custom("Input/Output", xarray_icon)


            # Raw Data

            Data = Custom("Data / Observations", files_icon)
            Files = Custom("Data", files_icon)
            NetCDF = Custom("NetCDF", netcdf_icon)
            #with Cluster('*On Disk'):
                #Zarr = Custom("Zarr store", zarr_icon)
            Zarr = Custom("Ordinary store", zarr_icon)

            with Cluster("Time Series"):

                with Cluster("SARAH 2/3 climate records"):
                    Global_Irradiance = Custom("Global\nHorizontal\nIrradiance\n(GHI)", irradiance_icon)
                    Direct_Irradiance = Custom("Direct\nHorizontal\nIrradiance\n(DHI)", irradiance_icon)
            
                with Cluster("ERA5 time series"):
                    Temperature = Custom("Temperature", temperature_icon)
                    Wind_Speed = Custom("Wind Speed", wind_speed_icon)

                Spectral_Effect = Custom("\nSpectral Factor", spectral_effect_icon)


            with Cluster("Data Pre-Processing PVGIS 6"):

                # Tools
                Kerchunk = Custom("Kerchunk", kerchunk_icon)

                with Cluster("Input Data Format"):
                    # Pre-Processed Data
                    Kerchunk_Reference_Set = Custom("Kerchunk Reference Set", binary_data_icon)

            with Cluster("Possible Input Data Formats"):
                HDF5 = Custom("HDF5", '')
                NetCDF
                Zarr
                CSV = Custom("CSV", '')
                GRIB = Custom("GRIB", '')
                # Virtual_Zarr = Custom("Virtual store", zarr_icon)

            with Cluster("Analysis of Photovoltaic Performance PVGIS 6"):
                Photovoltaic_Power = Custom("Photovoltaic Power", photovoltaic_power_icon)


            with Cluster("PVGIS <= 5.x"):

                with Cluster("Data Pre-Processing"):
                    Zarr

                with Cluster("Input Data Format"):
                    PVGIS_Time_Series = Custom("Only\nPVGIS-Native\nTime Series Format", binary_data_icon)

            with Cluster("Photovoltaic Performance Analysis PVGIS <=5.x"):
                #Photovoltaic_Power_PVGIS_5 = Custom("Photovoltaic Power PVGIS 5", photovoltaic_power_icon)
                Photovoltaic_Power_PVGIS_5 = Custom("Photovoltaic Energy\nPVGIS 5", photovoltaic_power_icon)

            # Workflow =======================================================

            # Format of Time Series Data

            Global_Irradiance >> NetCDF
            Direct_Irradiance >> NetCDF
            Temperature >> NetCDF
            Wind_Speed >> NetCDF
            Spectral_Effect >> NetCDF


            # PVGIS 6

            NetCDF \
            - Edge(label="Scan NetCDF files", color="red", style="dashed") \
            - Kerchunk \
            - Edge(label="Generate Reference Set", color="red", style="dashed") \
            - Kerchunk_Reference_Set \
            - Edge(label="Read with Zarr engine", color="red", style="dashed") \
            >> Xarray \
            >> PVGIS_6 \
            - NumPy \
            >> Photovoltaic_Power
            
            [NetCDF, HDF5, CSV, Zarr] \
            - Edge(label="Read NetCDF files", color="red", style="dashed") \
            >> Xarray


            # PVGIS 5.x

            Data \
            - Edge(label="Observations or modelled data", color="blue", style="dashed") \
            - NetCDF \
            - Edge(label="Provider's chunking", color="blue", style="dashed") \
            - Zarr \
            - Edge(label="from Massive Zarr store", color="blue", style="dashed") \
            - PVGIS_Time_Series \
            - Edge(label="Read with custom C code", color="blue", style="dashed") \
            >> PVGIS_5 \
            >> Photovoltaic_Power_PVGIS_5

            # Alternative 

            #Satellite_to_Data \
            #>> NetCDF

            #NetCDF \
            #- Edge(label="Observations or modelled data", color="blue", style="dashed") \
            #- Edge(label="Daily Data\nProducer's chunking", color="blue", style="dashed") \
            #- Edge(
            #        label="Rechunking to yearly time series\nMassive Transfer to Zarr Store\nData Duplication",
            #        color="blue", style="dashed"
            #      ) \
            #- Zarr \
            #- Edge(label="from (Massive!) Zarr store", color="blue", style="dashed") \
            #- PVGIS_Time_Series \
            #- Edge(label="PVGIS-Native time series format", color="blue", style="dashed") \
            #>> PVGIS_5 \
            #>> Photovoltaic_Power_PVGIS_5


            # Encode diagram as a PNG and print it in HTML Image format

            png = b64encode(diagram.dot.pipe(format="png")).decode()

    # Finally, print the "flow"

    print(f'<img src="data:image/png;base64, {png}"/>')

except Exception as e:
    print(f"An error occurred: {e}")

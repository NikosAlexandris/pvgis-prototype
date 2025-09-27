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
from diagrams import Diagram, Edge
from diagrams.custom import Custom
from diagrams.programming.flowchart import Action


# Icons 

icons_path = "docs/icons"

irradiance_icon = f"{icons_path}/wiggly_vertical_line.svg"
global_horizontal_irradiance_icon = f"{icons_path}/noun_global_horizontal_irradiance.svg"
direct_horizontal_irradiance_icon = f"{icons_path}/noun_direct_horizontal_irradiance.svg"
global_inclined_irradiance_icon = f"{icons_path}/noun_global_inclined_irradiance.svg"
direct_inclined_irradiance_icon = f"{icons_path}/noun_direct_normal_irradiance.svg"

sky_reflected_diffuse_irradiance_icon = f"{icons_path}/noun-scattered-material-366701.svg"
ground_reflected_diffuse_irradiance_icon = f"{icons_path}/noun_ground_reflected_irradiance.svg"

reflectivity_icon = f"{icons_path}/noun-reflection-5746443.svg"
spectral_effect_icon = f"{icons_path}/noun-sun-525998_modified.svg"
effective_irradiance_icon = f"{icons_path}/noun-solar-energy-6700671.svg"

thermometer_icon = f"{icons_path}/thermometer.svg"
temperature_effect_icon = thermometer_icon  # Find something else ?
temperature_icon = thermometer_icon  # Find something else ?
wind_speed_icon = "docs/icons/noun-windsock-4502486.svg"

photovoltaic_power_icon = f"{icons_path}/noun-solar-panel-6862742.svg"
system_loss_icon = f"{icons_path}/chart_with_downwards_trend.svg"
photovoltaic_power_output_icon = f"{icons_path}/noun-solar-energy-853048.svg"


try:
    with suppress(FileNotFoundError):
        graph_attr = {"splines":"spline", "fontsize": "30"}
        with Diagram(
                "Processing Solar Irradiance & Meteorological Variables",
                direction="TB",
                show=False,
                graph_attr=graph_attr
            ) as diagram:
            diagram.render = lambda: None

           # Solar_Altitude = Custom("Solar Altitude", '')
           # Sine_of_Solar_Altitude = Custom("sin(Solar Altitude)", '')

           # Solar_Azimuth = Custom("Solar Azimuth", '')
           # 
           # Solar_Incidence = Custom("Solar Incidence", '')
           # Complement_Solar_Incidence = Custom("Solar Incidence [Sun-to-Surface-Plane]", '')
           # Sine_of_Complement_Solar_Incidence = Custom("sin(Solar Incidence [Sun-to-Surface-Plane])", '')

           # Direct_Normal_Irradiance = Custom("Direct Normal Irradiance\(DNI)", '')
           # Direct_Horizontal_Irradiance = Custom("Direct Horizontal Irradiance\n(HI)", direct_horizontal_irradiance_icon)
            Direct_Inclined_Irradiance = Custom("Direct\nInclined Irradiance\n(HI)", direct_inclined_irradiance_icon)

           # Diffuse_Horizontal_Irradiance = Custom("Sky-Reflected Diffuse Horizontal Irradiance\n(HI)", irradiance_icon)
            Diffuse_Inclined_Irradiance = Custom("Sky-Reflected\nDiffuse\nInclined Irradiance\n(HI)", sky_reflected_diffuse_irradiance_icon)

            Ground_Reflected_Irradiance = Custom("Ground-Reflected\nDiffuse Irradiance\n(GRI)", ground_reflected_diffuse_irradiance_icon)

           # In_Plane_Irradiance = Custom("Global In-Plane Irradiance\n(GII)", irradiance_icon)

           # with Cluster("Irradiance Components Calculation"):
           #     direct_inclined_irradiance = Custom("Direct Inclined\nIrradiance", irradiance_icon)
           #     diffuse_inclined_irradiance = Custom("Diffuse Inclined\nIrradiance", irradiance_icon)
           #     ground_reflected_irradiance = Custom("Ground-Reflected\nIrradiance", irradiance_icon)

           # with Cluster("External Time Series Data"):

           #     with Cluster("SARAH 2/3 climate records"):
           #         Global_Horizontal_Irradiance = Custom("Global Horizontal Irradiance\n(GHI)", global_horizontal_irradiance_icon)
           #         Direct_Horizontal_Irradiance = Custom("Direct Horizontal Irradiance\n(DHI)", direct_horizontal_irradiance_icon)
           # 
           #     with Cluster("ERA5 Reanalysis Data"):
           #         Temperature = Custom("Temperature", temperature_icon)
           #         Wind_Speed = Custom("Wind Speed", wind_speed_icon)


            Global_Inclined_Irradiance = Custom("Global\nIn-Plane\nIrradiance", global_inclined_irradiance_icon)
           # reflectivity_loss = Custom("Reflectivity Loss\n(RE)", reflectivity_icon)
            

            # - Horizontal irradiance ~~ f(solar altitude & incidence angle) \~\~> In-Plane irradiance
            # - In-Plane irradiance ~~ Reflectivity Loss \~\~> In-Plane irradiance after reflectivity loss
            # - Irradiance afer loss due to the reflectivity effect ~~ Spectral Effect \~\~> Effective irradiance

            # Link nodes

            #normal_irradiance
            #horizontal_irradiance >> in_plane_irradiance >> reflectivity_loss >> effective_irradiance
            #effective_irradiance >> spectral_effect >> effective_irradiance
            #effective_irradiance >> temperature_low_irradiance_effect >> photovoltaic_power
            #photovoltaic_power >> system_loss >> final_power_output


            # global_horizontal_irradiance >> direct_inclined_irradiance
            # direct_horizontal_irradiance >> direct_inclined_irradiance
            # direct_inclined_irradiance >> effective_direct_irradiance

            # temperature >> diffuse_inclined_irradiance
            # wind_speed >> diffuse_inclined_irradiance
            # diffuse_inclined_irradiance >> effective_irradiance

            # spectral_factor >> ground_reflected_irradiance
            # ground_reflected_irradiance >> effective_irradiance

            #effective_irradiance >> efficiency
            #efficiency >> photovoltaic_power_without_loss
            #photovoltaic_power_without_loss >> system_loss
            #system_loss >> final_power_output


            # Calculation of Direct Inclined Irradiance ======================
           # Calculate_Direct_Inclined_Irradiance = Action(
           #     "Direct Horizontal Irradiance * sin(Solar Incidence [Sun-to-Surface-Plane]) / sin(Solar Altitude)"
           # )


           # Direct_Inclined_Irradiance \
           # << Calculate_Direct_Inclined_Irradiance \
           # - [
           #     Direct_Horizontal_Irradiance,
           #     Sine_of_Complement_Solar_Incidence,
           #     Sine_of_Solar_Altitude,
           #    ]

            # Components for Sky-Reflected Inclined Irradiance
            # cases for Diffuse Inclined Irradiance
           # Surface_in_Shade = Custom("Surface in Shade", '')
           # Sunlit_Surface = Custom("Sunlit Surface", '')
           # Potentially_Sunlit_Surface = Custom("Potentially Sunlit Surface", '')

            # Calculation of Sky-Reflected Diffuse Irradiance ================
           # Diffuse_Inclined_Irradiance \
           # << [
           #     Surface_in_Shade,
           #     Sunlit_Surface,
           #     Potentially_Sunlit_Surface,
           #    ]

            # Components for Ground-Reflected Irradiance
            Albedo = Custom("Albedo", '')
            Ground_View_Fraction = Custom("Ground View Fraction", '')

           # Calculation of Ground-Reflected Irradiance =====================
            Calculate_Ground_View_Fraction = Action(
                "Ground View Fraction =\n(1 - cos(Surface Tilt)) / 2"
            )
            Calculate_Ground_Reflected_Irradiance = Action(
                "Albedo * Global Horizontal Irradiance * Ground View Fraction"
            )
            Ground_Reflected_Irradiance \
            << Calculate_Ground_Reflected_Irradiance \
            << Calculate_Ground_View_Fraction \
            - [
                Albedo,
                Global_Horizontal_Irradiance,
                Ground_View_Fraction,
               ]

            Calculate_Global_Inclined_Irradiance = Action(
            "Direct Inclined + Diffuse Inclined + Ground-Reflected"
            )
            Global_Inclined_Irradiance \
            - Edge(color="blue", style="dashed") \
            << Calculate_Global_Inclined_Irradiance \
            - Edge(style="dashed") \
            - [
                Direct_Inclined_Irradiance,
                Diffuse_Inclined_Irradiance,
                Ground_Reflected_Irradiance,
               ]

            # Encode diagram as a PNG and print it in HTML Image format
            png = b64encode(diagram.dot.pipe(format="png")).decode()

    print(f'<img src="data:image/png;base64, {png}"/>')

except Exception as e:
    print(f"An error occurred: {e}")

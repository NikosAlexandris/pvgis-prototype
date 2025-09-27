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


path_to_icons = "docs/icons"
fractional_year_icon = f"{path_to_icons}/fractional-year.svg"
equation_of_time_icon = f"{path_to_icons}/noun-clock.svg"
time_offset_icon = f"{path_to_icons}/map-clock.svg"
true_solar_time_icon = f"{path_to_icons}/solar-time.svg"
solar_hour_angle_icon = f"{path_to_icons}/solar-hour-angle.svg"
solar_declination_icon = f"{path_to_icons}/earth_to_sun_angle.svg"
solar_zenith_icon = f"{path_to_icons}/solar-zenith.svg"
solar_altitude_icon = f"{path_to_icons}/sun-angle-outline.svg"
solar_azimuth_icon = f"{path_to_icons}/sun-compass.svg"
solar_incidence_icon = f"{path_to_icons}/noun_global_horizontal_irradiance_new.svg"


try:
    with suppress(FileNotFoundError):
        graph_attr = {
            # "splines": "spline",
            # "fontsize": "30",
            # "margin": "30"     # around the graph
        }
        node_attr = {
            # "fontsize": "30",
            # "shape": "box",
            # "fixedsize": "true",
            # "width": "2",
            # "height": "10",
        }
        with Diagram(
                "Calculation of Solar Position Parameters",
                 direction="RL",
                 show=False,
                 graph_attr=graph_attr,
                 node_attr=node_attr,
            ) as diagram:
            diagram.render = lambda: None

            Fractional_Year = Custom("Fractional Year", fractional_year_icon)
            Equation_of_Time = Custom("Equation of Time", equation_of_time_icon)
            Time_Offset = Custom("Time Offset", time_offset_icon)
            True_Solar_Time = Custom("True Solar Time", true_solar_time_icon)
            Solar_Hour_Angle = Custom("Solar Hour Angle", solar_hour_angle_icon)
            Solar_Declination = Custom("Solar Declination", solar_declination_icon)
            Solar_Zenith = Custom("Solar Zenith", solar_zenith_icon)
            Solar_Altitude = Custom("Solar Altitude", solar_altitude_icon)
            Solar_Azimuth = Custom("Solar Azimuth", solar_azimuth_icon)
            Solar_Incidence = Custom("Solar Incidence", solar_incidence_icon)

            Fractional_Year \
                << Equation_of_Time \
                << Time_Offset \
                << True_Solar_Time \
                << Solar_Hour_Angle

            Solar_Hour_Angle \
                << True_Solar_Time

            Solar_Declination \
                << Fractional_Year
            
            Solar_Zenith \
                << [Solar_Declination, Solar_Hour_Angle]

            Solar_Altitude \
                - Edge(style="dashed") \
                << Solar_Zenith

            Solar_Azimuth \
                << Solar_Zenith

            Solar_Azimuth \
                << Solar_Declination

            Solar_Incidence \
                    << [Solar_Zenith, Solar_Azimuth]

            png = b64encode(diagram.dot.pipe(format="png")).decode()

    print(f'<img src="data:image/png;base64, {png}"/>')

except Exception as e:
    print(f"An error occurred: {e}")

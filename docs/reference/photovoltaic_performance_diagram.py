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
from diagrams import Diagram, Edge, Cluster
from diagrams.custom import Custom


path_to_icons = "docs/icons"

global_inclined_irradiance_icon = f"{path_to_icons}/noun_global_inclined_irradiance.svg"
reflectivity_effect_icon = f"{path_to_icons}/reflectivity_effect_icon.svg"
spectral_effect_icon = f"{path_to_icons}/noun-sun-525998_modified.svg"
effective_irradiance_icon = f"{path_to_icons}/noun-solar-energy-6700671.svg"
temperature_and_low_irradiance_effect_icon = f"{path_to_icons}/thermometer.svg"
wind_speed_icon = "docs/icons/noun-windsock-4502486.svg"
photovoltaic_power_icon = f"{path_to_icons}/noun-solar-panel-6862742.svg"
system_loss_icon = f"{path_to_icons}/chart_with_downwards_trend.svg"
final_power_output_icon = f"{path_to_icons}/noun-solar-energy-853048.svg"


try:
    with suppress(FileNotFoundError):
        graph_attr = {"splines":"spline"}
        with Diagram("Analysis of Photovoltaic Performance", direction="TB", show=False, graph_attr=graph_attr) as diagram:
            diagram.render = lambda: None

            # Custom nodes
            in_plane_irradiance = Custom("In-Plane Irradiance\n(II)", global_inclined_irradiance_icon)
            effective_irradiance = Custom("Effective Irradiance\n(EI) = II + RE + SE", effective_irradiance_icon)
            photovoltaic_power = Custom("Photovoltaic Power\n(PP) = EI + TE", photovoltaic_power_icon)
            final_power_output = Custom("Final Photovoltaic Power/Energy Output\n∑PP = PP + SL", final_power_output_icon)


            with Cluster("Effects"):
                reflectivity_effect = Custom("Reflectivity =\n 𝑓 (Incidence)", reflectivity_effect_icon)
                spectral_effect = Custom("\nSpectral Factor", spectral_effect_icon)

                temperature_and_low_irradiance_effect = Custom("Module Temperature =\n 𝑓 (Air Temperature, Wind Speed)", temperature_and_low_irradiance_effect_icon)
                system_loss = Custom("System Loss", system_loss_icon)


            # Link the nodes to visualize the workflow
            in_plane_irradiance \
            - Edge(label="Reflectivity Effect\n(RE)", color="firebrick", style="dashed") \
            - reflectivity_effect \
            >> Edge(label="RE = II * Reflectivity", color="firebrick", style="dashed") \
            >> effective_irradiance


            in_plane_irradiance \
            - Edge(label="Spectral Effect\n(SE)", color="orange", style="dashed") \
            - spectral_effect \
            >> Edge(label="SE = II * Spectral Factor", color="orange", style="dashed") \
            >> effective_irradiance


            effective_irradiance \
            - Edge(label="Temperature & Low Irradiance Effect\n(TE)", color="red", style="dashed") \
            - temperature_and_low_irradiance_effect \
            >> Edge(label="TE = EI * Efficiency Coefficients", color="red", style="dashed") \
            >> photovoltaic_power


            photovoltaic_power \
            - Edge(label="System Loss (SL)", color="magenta", style="dashed") \
            - system_loss \
            >> Edge(label="SL = P * System Loss Factor", color="magenta") \
            >> final_power_output


            # Encode diagram as a PNG and print it in HTML Image format
            png = b64encode(diagram.dot.pipe(format="png")).decode()

    print(f'<img src="data:image/png;base64, {png}"/>')

except Exception as e:
    print(f"An error occurred: {e}")

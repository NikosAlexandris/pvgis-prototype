from base64 import b64encode
from contextlib import suppress
from diagrams import Diagram, Edge
from diagrams.custom import Custom


path_to_icons = "docs/icons"
fractional_year_icon = f"{path_to_icons}/radius-outline.svg"
equation_of_time_icon = f"{path_to_icons}/sun-angle-outline.svg"
time_offset_icon = f"{path_to_icons}/map-clock.svg"
true_solar_time_icon = f"{path_to_icons}/solar-time.svg"
solar_hour_angle_icon = f"{path_to_icons}/sun-clock.svg"
solar_declination_icon = f"{path_to_icons}/weather-sunset.svg"
solar_zenith_icon = f"{path_to_icons}/weather-sunny.svg"
solar_altitude_icon = f"{path_to_icons}/weather-partly-cloudy.svg"
solar_azimuth_icon = f"{path_to_icons}/weather-sunset-up.svg"


try:
    with suppress(FileNotFoundError):
        graph_attr = {"splines":"spline", "fontsize": "30"}
        node_attr = {"fontsize": "30"}
        with Diagram(
                "Solar Position Calculation Sequence",
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
            Solar_Incidence = Custom("Solar Incidence", '')

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

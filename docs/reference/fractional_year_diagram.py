from base64 import b64encode
from contextlib import suppress
from diagrams import Diagram
from diagrams.custom import Custom
from diagrams.programming.flowchart import Action


path_to_icons = "docs/icons"
fractional_year_icon = f"{path_to_icons}/radius-outline.svg"
equation_of_time_icon = f"{path_to_icons}/sun-angle-outline.svg"
time_offset_icon = f"{path_to_icons}/sun-wireless-outline.svg"
true_solar_time_icon = f"{path_to_icons}/sun-compass.svg"
solar_hour_angle_icon = f"{path_to_icons}/sun-clock.svg"
solar_declination_icon = f"{path_to_icons}/weather-sunset.svg"
solar_zenith_icon = f"{path_to_icons}/weather-sunny.svg"
solar_altitude_icon = f"{path_to_icons}/weather-partly-cloudy.svg"
solar_azimuth_icon = f"{path_to_icons}/weather-sunset-up.svg"


try:
    with suppress(FileNotFoundError):
        with Diagram("Solar Position Calculation Sequence", direction="RL", show=False) as diagram:
            diagram.render = lambda: None

            Fractional_Year = Custom("Fractional Year", fractional_year_icon)

            Days_in_Years = Custom("Days in Years", '')
            Days_of_Year = Custom("Days of Year", '')
            Hours = Custom("Hours", '')
            Zero_Negative_Fractional_Year = Action("FY = 0 if FY < 0")

            # fractional_year_series = np.array(
            #     2 * np.pi / days_in_years * (days_of_year - 1 + (hours - 12) / 24),
            #     dtype=dtype,
            # )
            # # Is this "restriction" correct ?
            # fractional_year_series[fractional_year_series < 0] = 0

            Fractional_Year \
            - Zero_Negative_Fractional_Year \
            << [Days_in_Years, Days_of_Year, Hours]

            png = b64encode(diagram.dot.pipe(format="png")).decode()

        print(f'<img src="data:image/png;base64, {png}"/>')


except Exception as e:
    print(f"An error occurred: {e}")

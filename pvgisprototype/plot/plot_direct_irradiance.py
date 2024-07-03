import matplotlib.pyplot as plt


def plot_direct_inclined_irradiance_over_day(
    latitude,
    elevation,
    date,
    linke_turbidity_factor,
    method_for_solar_incidence_angle,
    surface_tilt=0,
    surface_orientation=180,
):
    irradiance_values = []
    timestamps = []

    for hour in range(24):  # For each hour in the day
        timestamp = datetime(year=date.year, month=date.month, day=date.day, hour=hour)
        direct_irradiance = calculate_direct_inclined_irradiance(
            latitude=latitude,
            elevation=elevation,
            timestamp=timestamp,
            linke_turbidity_factor=linke_turbidity_factor,
            method_for_solar_incidence_angle=method_for_solar_incidence_angle,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
        )
        timestamps.append(timestamp)
        irradiance_values.append(direct_irradiance)

    plt.plot(timestamps, irradiance_values)
    plt.xlabel("Time")
    plt.ylabel("Direct Inclined Irradiance (W/m^2)")
    plt.title("Direct Inclined Irradiance Over Day")
    plt.show()

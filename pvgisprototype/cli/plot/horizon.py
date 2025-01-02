import numpy as np
from typing import List
from numpy import where, nan
from uniplot import plot
from numpy.typing import NDArray


def plot_horizon_profile(
    azimuthal_directions_degrees,
    horizon_profile_degrees,
    label="Horizon",
    color="cyan",
):
    """
    Plot a horizon height profile dynamically in polar coordinates.

    Parameters
    ----------
    - azimuthal_directions_degrees: Azimuthal directions in degrees (0-360).
    - horizon_profile_degrees: Horizon height angles in degrees corresponding to azimuthal directions.
    - label: Label for the plot legend.
    - color: Color for the plot line.

    Acknowledgment
    --------------
    Some assistance by :
    - Olav Stetter
    - Chrysa Stathaki
    
    """
    # Convert azimuthal directions and horizon profile to radians
    azimuthal_directions_radians = np.radians(azimuthal_directions_degrees)
    # flat_horizon_profile_radians = np.full(azimuthal_directions_degrees.shape, np.pi/2)
    horizon_profile_radians = np.radians(horizon_profile_degrees)

    # Calculate polar coordinates (x, y) for the horizon profile
    # x_horizon_flat = np.sin(azimuthal_directions_radians) * flat_horizon_profile_radians
    x_horizon_flat = np.sin(azimuthal_directions_radians) * np.pi/2
    # y_horizon_flat = np.cos(azimuthal_directions_radians) * flat_horizon_profile_radians
    y_horizon_flat = np.cos(azimuthal_directions_radians) * np.pi / 2
    x_horizon = x_horizon_flat - np.sin(azimuthal_directions_radians) * horizon_profile_radians
    y_horizon = y_horizon_flat - np.cos(azimuthal_directions_radians) * horizon_profile_radians

    plot(
        xs=azimuthal_directions_degrees,
        ys=horizon_profile_degrees,
        lines=True,
        width=45,
        height=4,
        x_gridlines=[],
        y_gridlines=[],
        color=color,
        legend_labels=["Horizon Profile"],
    )

    # Plot the horizon profile in Cartesian space
    # print(f'Flat Horizon x : {x_horizon_flat}')
    # print(f'Flat Horizon y : {y_horizon_flat}')
    # print(f'Horizon x : {x_horizon}')
    # print(f'Horizon y : {y_horizon}')
    plot(
        xs=[
            x_horizon_flat,
            x_horizon,
            ],
        ys=[
            y_horizon_flat,
            y_horizon,
            ],
        lines=[False, True],
        width=45,
        height=20,
        x_gridlines=[],
        y_gridlines=[],
        color=["cyan", color],
        legend_labels=["Horizon", label],
        character_set="braille",
    )
    # plot(
    #     xs=x_horizon,
    #     ys=y_horizon,
    #     lines=True,
    #     width=45,
    #     height=20,
    #     x_gridlines=[],
    #     y_gridlines=[],
    #     color=[color],
    #     legend_labels=[label],
    #     character_set="braille",
    # )


def plot_horizon_profile_x(
    solar_position_series: dict,
    horizon_profile: NDArray,
    labels: List[str],
    colors=["cyan", "blue", "yellow"],
):
    """
    Plot a horizon height profile dynamically in polar coordinates.

    Parameters
    ----------
    - azimuthal_directions_degrees: Azimuthal directions in degrees (0-360).
    - series_in_degrees: Series of (angular) measurements in degrees corresponding to azimuthal directions.
    - label: Label for the plot legend.
    - color: Color for the plot line.
    """
    from pvgisprototype.cli.print.helpers import get_value_or_default
    from pvgisprototype.api.position.models import (
        SolarPositionParameter,
    )

    # Generate equidistant azimuthal directions

    azimuthal_directions_radians = np.linspace(0, 2 * np.pi, horizon_profile.size)

    # Calculate polar coordinates (x, y) for the horizon + profile

    horizon_profile_radians = np.radians(horizon_profile)  # input in degrees
    x_horizontal_plane = np.sin(azimuthal_directions_radians) * np.pi / 2
    y_horizontal_plane = np.cos(azimuthal_directions_radians) * np.pi / 2
    x_horizon = x_horizontal_plane - np.sin(azimuthal_directions_radians) * horizon_profile_radians
    y_horizon = y_horizontal_plane - np.cos(azimuthal_directions_radians) * horizon_profile_radians
    plot(
        xs=np.degrees(azimuthal_directions_radians),
        ys=horizon_profile,
        lines=True,
        width=45,
        height=4,
        x_gridlines=[],
        y_gridlines=[],
        color=[colors[1]],
        legend_labels=[labels[1]],
    )

    # Loop over possibly multiple solar positioning algorithms ?

    for model_name, model_result in solar_position_series.items():

        # Get altitude

        solar_altitude_in_radians = get_value_or_default(
                model_result,
                SolarPositionParameter.altitude
                )

        # Mask values outside the azimuth circle.  Attention : overwrite original variables !
        solar_altitude_in_radians = where(
                solar_altitude_in_radians >= 0,
                solar_altitude_in_radians,
                nan
        )

        # Get azimuth

        solar_azimuth_radians = get_value_or_default(
                model_result,
                SolarPositionParameter.azimuth
                )
        # Convert solar azimuth in degrees series to radians

        # Calculate polar coordinates (x, y) for solar azimuth and altitude

        x_solar_azimuth = np.sin(solar_azimuth_radians) * np.pi / 2
        y_solar_azimuth = np.cos(solar_azimuth_radians) * np.pi / 2

        x_polar_solar_altitude = x_solar_azimuth - np.sin(solar_azimuth_radians) * solar_altitude_in_radians
        y_polar_solar_altitude = y_solar_azimuth - np.cos(solar_azimuth_radians) * solar_altitude_in_radians

        x_series = [
            x_horizontal_plane,
            x_horizon,
            x_polar_solar_altitude,
        ]
        y_series = [
            y_horizontal_plane,
            y_horizon,
            y_polar_solar_altitude,
        ]

        # Plot the horizon profile polar coordinates in Cartesian space
        plot(
            xs=x_series,
            ys=y_series,
            lines=[True, True, False],
            width=45,
            height=20,
            x_gridlines=[],
            y_gridlines=[],
            color=colors,
            legend_labels=labels,
            character_set="braille",
        )

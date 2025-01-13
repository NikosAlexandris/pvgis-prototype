import numpy as np
from typing import List
from numpy import where, nan
from uniplot import plot
from numpy.typing import NDArray


def plot_horizon_profile_x(
    solar_position_series: dict,
    horizon_profile: NDArray,
    labels: List[str],
    colors=["cyan", "blue", "yellow"],
):
    
    """
    Plot a horizon height profile dynamically in polar coordinates along with
    positions of the sun in the sky (solar altitude).

    Parameters
    ----------
    solar_position_series : dict
        Dictionary containing solar position data.
    horizon_profile : NDArray
        Array of horizon height values corresponding to azimuth angles.
    labels : List[str]
        List of labels for the plot legend.
    colors : List[str], optional
        List of colors for plotting different series (default is ["cyan", "blue", "yellow"]).

    Notes
    -----
    This function creates a polar plot showing the horizon height profile
    around a given geographic location and positions of the sun in the sky
    (solar altitude). The horizon height profile is represented as a radial
    plot, where the radial distance starting from the outer perimeter
    (horizontal plane circle) corresponds to the horizon height, and the
    clock-wise angle starting from the top center of the polar plot (0 degrees
    = North) represents the azimuthal direction.

    Examples
    --------
    To use this function via the command line:

    >>> pvgis-prototype position overview 7.9672 45.9684 --start-time "2010-06-15 05:00:00" --end-time "2010-06-15 20:00:00"  --horizon-profile horizon_12_076.zarr --horizon-plot

    This command will generate a polar plot, as shown below, showing the
    horizon profile and solar positions for the requested location and period.

    ┌─────────────────────────────────────────────┐
    │             ⣀⠤⠤⠒⠒⢀⡠⣀⣀⡀⠉⠉⠉⠉⠒⠒⠤⠤⣀             │
    │         ⣀⠤⠒⠉ ⣀⡠⠔⠒⠁   ⠠⣀⡀       ⠉⠒⠤⣀         │
    │      ⢀⠤⠊  ⢀⠖⠉          ⠈⠑⠢⢄⡀       ⠑⠤⡀      │
    │    ⢀⠔⠁ ⢀⡠⠒⠁                ⠈⠓⠤⡀      ⠈⠢⡀    │
    │   ⢀⠁ ⢀⡐⠉                      ⠈⠢⣀      ⠈⢆   │
    │  ⡜  ⢀⡜                           ⠑⣄      ⢣  │
    │ ⡜  ⡀⢸                              ⢢   ⢀  ⢣ │
    │⢰⠁   ⡜                               ⢇     ⠈⡆│
    │⡇    ⠐                               ⠈⡆⠄    ⢸│
    │⡇    ⢱ ⢀                            ⢀ ⡇     ⢸│
    │⡇     ⢣   ⢀                       ⡀  ⢠⠃     ⢸│
    │⡇      ⢣     ⠠                 ⠄     ⡎      ⢸│
    │⢸⡀     ⢸         ⠁  ⠐   ⠄  ⠐        ⢰⠁     ⢀⡇│
    │ ⢣      ⢣                          ⡔⠁      ⡜ │
    │  ⢣      ⠡⡄                       ⡸       ⡜  │
    │   ⠱⡀     ⠈⢆                    ⠠⠊      ⢀⠎   │
    │    ⠈⠢⡀     ⠑⠢⢄⡀            ⢀⡠⠔⠊⠁     ⢀⠔⠁    │
    │      ⠈⠢⢄      ⠈⠑⠢⢄⣀⣀⣀⣀⣀⠤⠒⠉⠉⠁       ⡠⠔⠁      │
    │         ⠉⠢⢄⡀                   ⢀⡠⠔⠉         │
    │            ⠈⠉⠒⠢⠤⢄⣀⣀⣀⣀⣀⣀⣀⣀⣀⡠⠤⠔⠒⠉⠁            │
    └─────────────────────────────────────────────┘

    Acknowledgment
    --------------
    Some assistance by :
    - Olav Stetter
    - Chrysa Stathaki

    """
    from pvgisprototype.cli.print.helpers import get_value_or_default
    from pvgisprototype.api.position.models import (
        SolarPositionParameter,
    )

    # Generate equidistant azimuthal directions

    azimuthal_directions_radians = np.linspace(0, 2 * np.pi, horizon_profile.size)
    plot(
        xs=np.degrees(azimuthal_directions_radians),
        ys=horizon_profile,
        lines=True,
        width=45,
        height=3,
        x_gridlines=[],
        y_gridlines=[],
        color=[colors[1]],
        legend_labels=[labels[1]],
        character_set="braille",
    )

    # Calculate polar coordinates (x, y) for the horitontal plane and horizon height profile

    # horizon_profile_radians = np.radians(horizon_profile)  # input in degrees
    x_horizontal_plane = np.sin(azimuthal_directions_radians) * np.pi / 2
    y_horizontal_plane = np.cos(azimuthal_directions_radians) * np.pi / 2
    x_horizon = x_horizontal_plane - np.sin(azimuthal_directions_radians) * horizon_profile_radians
    y_horizon = y_horizontal_plane - np.cos(azimuthal_directions_radians) * horizon_profile_radians

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

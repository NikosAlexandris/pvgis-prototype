"""
energy
    grid
        - fixed
        - tracking
    off-grid
"""

import os
import pathlib
from typing import List

import typer
from rich import print
from typing_extensions import Annotated

from pvgisprototype.cli.messages import NOT_IMPLEMENTED
from pvgisprototype.cli.typer_parameters import (
    typer_argument_horizon_heights,
    typer_argument_latitude,
    typer_argument_longitude,
    typer_argument_mounting_type,
    typer_argument_pv_technology,
    typer_argument_surface_orientation,
    typer_argument_surface_tilt,
    typer_option_optimise_surface_geometry,
    typer_option_optimise_surface_tilt,
)
from pvgisprototype.constants import (
    OPTIMISE_SURFACE_GEOMETRY_FLAG_DEFAULT,
    OPTIMISE_SURFACE_TILT_FLAG_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
)

from .example_pv_estimation_output import csv_to_list_of_dictionaries

app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":sun::high_voltage: Estimate the energy production of a PV system {NOT_IMPLEMENTED}",
)


@app.command(
    "grid",
    no_args_is_help=True,
    help=f":electric_plug: Estimate the energy production of a PV system connected to the electricity grid {NOT_IMPLEMENTED}",
)
def estimate_grid_connected_pv(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    peak_power: Annotated[
        float,
        typer.Argument(
            rich_help_panel="Required",
            help="The installed peak PV power in kWp",
            min=0,
            max=100000000,
        ),
    ],  # peakpower
    loss: Annotated[
        float,
        typer.Argument(
            rich_help_panel="Preset", help="System losses in %", min=0, max=100
        ),
    ] = 14,  # loss
    solar_radiation_database: Annotated[
        str | None,
        typer.Argument(
            rich_help_panel="Preset",
            help="Solar radiation database with hourly time resolution",
        ),
    ] = "PVGIS-SARAH2",  # raddatabase
    consider_shadows: Annotated[
        bool,
        typer.Argument(
            rich_help_panel="Preset", help="Calculate effect of horizon shadowing"
        ),
    ] = True,  # usehorizon
    horizon_heights: Annotated[List[float], typer_argument_horizon_heights] = None,
    pv_techonology: Annotated[
        str | None, typer_argument_pv_technology
    ] = None,  # pvtechchoice
    mounting_type: Annotated[str | None, typer_argument_mounting_type] = "free",
    surface_orientation: Annotated[
        float, typer_argument_surface_orientation
    ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[float, typer_argument_surface_tilt] = SURFACE_TILT_DEFAULT,
    optimise_surface_tilt: Annotated[
        bool, typer_option_optimise_surface_tilt
    ] = OPTIMISE_SURFACE_TILT_FLAG_DEFAULT,
    optimise_surface_geometry: Annotated[
        bool, typer_option_optimise_surface_geometry
    ] = OPTIMISE_SURFACE_GEOMETRY_FLAG_DEFAULT,
    single_axis_system: Annotated[
        bool,
        typer.Argument(
            rich_help_panel="Optional",
            help="Consider a single axis PV system -- Remove Me and improve single_axis_inclination!",
        ),
    ] = False,  # inclined_axis
    single_axis_inclination: Annotated[
        float,
        typer.Argument(
            rich_help_panel="Optional",
            help="Inclination for a single axis PV system",
            min=0,
            max=90,
        ),
    ] = 0,  # inclinedaxisangle
    optimise_single_axis_inclination: Annotated[
        bool,
        typer.Argument(
            rich_help_panel="Optional",
            help="Optimise inclination for a single axis PV system",
        ),
    ] = False,  # inclined_optimum
    vertical_axis_system: Annotated[
        bool,
        typer.Argument(
            rich_help_panel="Optional",
            help="Consider a single vertical axis PV system -- Remove Me and improve vertical_axis_inclination!",
        ),
    ] = False,  # vertical_axis
    vertical_axis_inclination: Annotated[
        float,
        typer.Argument(
            rich_help_panel="Optional",
            help="Inclination for a single axis PV system",
            min=0,
            max=90,
        ),
    ] = 0,  # Verticalaxisangle
    optimise_vertical_axis_inclination: Annotated[
        bool,
        typer.Argument(
            rich_help_panel="Optional",
            help="Optimise inclination for a single vertical axis PV system",
        ),
    ] = False,  # vertical_optimum
    two_axis_system: Annotated[
        bool,
        typer.Argument(
            rich_help_panel="Optional",
            help="Consider a two-axis tracking PV system -- Review Me!",
        ),
    ] = False,  # twoaxis
    electricity_price: Annotated[
        bool,
        typer.Argument(
            rich_help_panel="Optional",
            help="Calculate the PV electricity price (kwh/year) for the system cost in the user requested currency -- Review Me!",
        ),
    ] = False,  # pvprice
    cost: Annotated[
        float,
        typer.Argument(
            rich_help_panel="Optional",
            help="Total cost of installing the PV system [custom currency]",
            min=0,
            max=100000000,
        ),
    ] = 0,  # systemcost
    interest: Annotated[
        float,
        typer.Argument(
            rich_help_panel="Optional", help="Interest in %/year", min=0, max=100
        ),
    ] = None,  # interest
    lifetime: Annotated[
        int,
        typer.Argument(
            rich_help_panel="Optional",
            help="Expected lifetime of the PV system in years",
            min=0,
            max=100,
        ),
    ] = 25,  # lifetime
    output_format: Annotated[
        str | None, typer.Argument(help="Output format")
    ] = "csv",  # outputformat
):
    r"""Estimate the energy production of a PV system connected to the electricity grid

    Performance of grid-connected PV systems.  This tool makes it possible to
    estimate the average monthly and yearly energy production of a PV system
    connected to the electricity grid, without battery storage. The calculation
    takes into account the solar radiation, temperature, wind speed and type of
    PV module. The user can choose how the modules are mounted, whether on a
    free-standing rack mounting, sun-tracking mountings or integrated in a
    building surface. PVGIS can also calculate the optimum slope and
    orientation that maximizes the yearly energy production.

    Requires following data:

        - elevation
        - horizon
        - dem_era5
        - tgrad_bin
        - sis
        - sid
        - temperature (ERA5 t2m)
        - wind speed (ERA5 w2m)
        - pv coefficients (current file: pvtech.coeffs)
        - pv coefficients for bifacial? (current file: pvtech.coeffs_bipv)
        - spectral correction data (current file: pvtech_spectraldata.bin)

    Parameters
    ----------
    longitude: float
    latitude: float
    peak_power: float
    loss: float
    solar_radiation_database: {'PVGIS-SARAH2', 'PVGIS-SARAH', 'PVGIS-NSRDB', 'PVGIS-ERA5'}, optional
    consider_shadows: bool
    horizon_heights: int
    pv_techonology: str
    mounting_type: str
    inclination: float
    orientation: float
    optimise_inclination: bool
    optimise_angles: bool
    single_axis_system: bool
    single_axis_inclination: float
    optimise_single_axis_inclination: bool
    vertical_axis_system: bool
    vertical_axis_inclination: float
    optimise_vertical_axis_inclination: bool
    two_axis_system: bool
    electricity_price: bool
    cost: float
    interest: float
    lifetime: int
    output_format: str

    Other Parameters
    ----------------
    only_seldom_used_keyword : int, optional
        Infrequently used parameters can be described under this optional
        section to prevent cluttering the Parameters section.
    **kwargs : dict
        Other infrequently used keyword arguments. Note that all keyword
        arguments appearing after the first parameter specified under the
        Other Parameters section, should also be described under this
        section.

    Returns
    -------
    str
        PV calculation result based on the specified input parameters

    Raises
    ------
    BadException
        Because you shouldn't have done that.

    See Also
    --------
    estimate_energy.offgrid : Relationship (optional).

    Notes
    -----

    The following notes are sourced from:

    - the manual of PVcalc
    - the web GUI
    - the original C/C++ program `rsun_standalone_hourly_opt`

    Original Parameters:

    - lat (float): Latitude in decimal degrees, south is negative. (Required)
    - lon (float): Longitude in decimal degrees, west is negative. (Required)

        - Input latitude and longitude

        Latitude and longitude can be input in the format DD:MM:SSA where
        DD is the degrees, MM the arc-minutes, SS the arc-seconds and A the
        hemisphere (N, S, E, W).

        Latitude and longitude can also be input as decimal values, so for
        instance 45°15'N should be input as 45.25. Latitudes south of the
        equator are input as negative values, north are positive.
        Longitudes west of the 0° meridian should be given as negative
        values, eastern values are positive.

    - peakpower (float): Nominal power of the PV system in kW. (Required)

        - Installed peak PV power [kWp] - Peak power

        This is the power that the manufacturer declares that the PV array
        can produce under standard test conditions, which are a constant
        1000W of solar irradiance per square meter in the plane of the
        array, at an array temperature of 25°C. The peak power should be
        entered in kilowatt-peak (kWp). If you do not know the declared
        peak power of your modules but instead know the area of the modules
        (in m2) and the declared conversion efficiency (in percent), you
        can calculate the peak power as power (kWp) = 1 kW/m2 * area *
        efficiency / 100. See more explanation in the FAQ

    - loss (float): Sum of system losses in percent. (Required)

        - Estimated system losses

        The estimated system losses are all the losses in the system, which
        cause the power actually delivered to the electricity grid to be
        lower than the power produced by the PV modules. There are several
        causes for this loss, such as losses in cables, power inverters,
        dirt (sometimes snow) on the modules and so on. Over the years the
        modules also tend to lose a bit of their power, so the average
        yearly output over the lifetime of the system will be a few percent
        lower than the output in the first years.

        We have given a default value of 14% for the overall losses. If you
        have a good idea that your value will be different (maybe due to a
        really high-efficiency inverter) you may reduce this value a
        little.

    - raddatabase (str): Radiation database. (Default: "PVGIS-SARAH2")

        - Solar radiation databases

        - PVGIS offers four different solar radiation databases with hourly
          time resolution. At the moment, there are three satellite-based
          databases:

          - PVGIS-SARAH2 (0.05º x 0.05º) Database produced by CM SAF to
            replace SARAH-1 (PVGIS-SARAH). It covers Europe, Africa, most
            of Asia, and parts of South America. Temporal range: 2005-2020.

          - PVGIS-SARAH* (0.05º x 0.05º) Database produced using the CM SAF
            algorithm. Similar coverage to SARAH-2. Temporal range:
            2005-2016.

          - PVGIS-NSRDB (0.04º x 0.04º) Result of a collaboration with NREL
            (USA) under which the NSRDB solar radiation database was made
            available for PVGIS. Temporal range: 2005-2015.

        In addition to these, there is also a reanalysis database available
        worldwide.

          - PVGIS-ERA5 (0.25º x 0.25º) Latest global reanalysis of the
            ECMWF (ECMWF). Temporal range: 2005-2020.

        Reanalyses solar radiation data generally have larger uncertainty
        than satellite-based databases. Therefore, we recommend using
        reanalysis data only where satellite-based data are missing or
        outdated. For more information about the databases and the
        accuracy, see the PVGIS web page on the calculation methods.


    - usehorizon (int): Consider shadows from high horizon (1) or not (0). (Default: 1)

        - Calculated horizon

        The solar radiation and PV output will change if there are local
        hills or mountains that block the light of the sun during some
        periods of the day. PVGIS can calculate the effect of this using
        data about ground elevation with a resolution of 3 arc-seconds
        (around 90m). This calculation does not take into account shadows
        from very nearby objects such as houses or trees. In this case you
        can upload your own horizon information.

        It is normally a good idea to use the horizon shadowing option.

    - userhorizon (list): Height of the horizon at equidistant directions
      around the point of interest, in degrees. Starting at north and
      moving clockwise. (Optional)

        - User-defined horizon

        PVGIS includes a database of the horizon height around each point
        you can choose in the region. In this way, the calculation of PV
        performance can take into account the effects of mountains and
        hills casting shadows onto the PV system. The resolution of the
        horizon information is 3 arc-seconds (around 90m), so objects that
        are very near, such as houses or trees are not included. However,
        you have the possibility to upload your own information about the
        horizon height.

        The horizon file to be uploaded to our web site should be a simple
        text file, such as you can create using a text editor (such as
        Notepad for Windows), or by exporting a spreadsheet as
        comma-separated values (.csv). The file name must have the
        extensions '.txt' or '.csv'.

        In the file there should be one number per line, with each number
        representing the horizon height in degrees in a certain compass
        direction around the point of interest. The horizon height cannot
        be higher than 90 degrees, so if the file contains a value higher
        than that, it will be automatically replaced by 90.

        The horizon heights in the file should be given in a clockwise
        direction starting at North; that is, from North, going to East,
        South, West, and back to North. The values are assumed to represent
        equal angular distance around the horizon. For instance, if you
        have 36 values in the file, PVGIS assumes that the first point is
        due north, the next is 10 degrees east of north, and so on, until
        the last point, 10 degrees west of north.

        An example file can be found here. In this case, there are only 12
        numbers in the file, corresponding to a horizon height for every 30
        degrees around the horizon.

    - pvtechchoice (str): PV technology choice. (Optional)

        - PV technology

        The performance of PV modules depends on the temperature and on the
        solar irradiance, as well as on the spectrum of the sunlight, but
        the exact dependence varies between different types of PV modules.
        At the moment we can estimate the losses due to temperature and
        irradiance effects for the following types of modules:

            1. crystalline silicon cells
            - thin film modules made from:
              2. CIS or CIGS
              3. Cadmium Telluride (CdTe)

        For other technologies (especially various amorphous technologies),
        this correction cannot be calculated here. If you choose one of the
        first three options here the calculation of performance will take
        into account the temperature dependence of the performance of the
        chosen technology. If you choose the other option (other/unknown),
        the calculation will assume a loss of 8% of power due to
        temperature effects (a generic value which was found to be
        reasonable for temperate climates). Note that the calculation of
        the effect of spectral variations is at the moment only available
        for crystalline silicon and for CdTe. The spectral effect cannot be
        considered yet for the areas only covered by the PVGIS-NSRDB
        database.


    - mountingplace (str): Type of mounting of the PV modules. Choices are: "free" or "building". (Default: "free")

    - fixed (bool): Calculate a fixed mounted system (1) or not (0). (Default: 1)

        - Mounting position

        For fixed (non-tracking) systems, the way the modules are mounted
        will have an influence on the temperature of the module, which in
        turn affects the efficiency. Experiments have shown that if the
        movement of air behind the modules is restricted, the modules can
        get considerably hotter (up to 15°C at 1000W/m2 of sunlight).

        In the application there are two possibilities: free-standing,
        meaning that the modules are mounted on a rack with air flowing
        freely behind the modules; and roof added / building-integrated,
        which means that the modules are completely built into the
        structure of the wall or roof of a building, with little or no air
        movement behind the modules.

        Some types of mounting are in between these two extremes, for
        instance if the modules are mounted on a roof with curved roof
        tiles, allowing air to move behind the modules. In such cases, the
        performance will be somewhere between the results of the two
        calculations that are possible here. For such cases, to be
        conservative, the roof added / building integrated option can be
        used.

    - angle (float): Inclination angle from horizontal plane of the fixed PV system. (Optional)

        - Inclination angle or slope

        This is the angle of the PV modules from the horizontal plane, for
        a fixed (non-tracking) mounting.

        For some applications the slope and orientation angles will already
        be known, for instance if the PV modules are to be built into an
        existing roof. However, if you have the possibility to choose the
        slope and/or azimuth (orientation), this application can also
        calculate for you the optimal values for slope and orientation
        (assuming fixed angles for the entire year).

    - aspect (float): Orientation (azimuth) angle of the fixed PV system. (Optional)

        - Orientation angle or azimuth

        The azimuth, or orientation, is the angle of the PV modules
        relative to the direction due South. -90° is East, 0° is South and
        90° is West.

        For some applications the slope and azimuth angles will already be
        known, for instance if the PV modules are to be built into an
        existing roof. However, if you have the possibility to choose the
        inclination and/or orientation, this application can also calculate
        for you the optimal values for inclination and orientation
        (assuming fixed angles for the entire year).

    - optimalinclination (bool): Calculate the optimum inclination angle (1) or not (0). (Optional)

        - Optimize slope

        If you click to choose this option, PVGIS will calculate the slope
        of the PV modules that gives the highest energy output for the
        whole year. This assumes that the slope angle stays fixed for the
        entire year.

    - optimalangles (bool): Calculate the optimum inclination and orientation angles (1) or not (0). (Optional)

        - Optimize inclination and azimuth

        If you click to choose this option, PVGIS will calculate the
        inclination AND orientation/azimuth of the PV modules that gives
        the highest energy output for the whole year. This assumes that the
        mounting of the PV modules stays fixed for the entire year.

    - inclined_axis (bool): Calculate a single inclined axis system (1) or not (0). (Optional)

        - Inclined Axis

        In this type of PV system, the modules are mounted on a structure
        rotating around an axis that forms an angle with the ground and
        points in the north-south direction. The plane of the modules is
        assumed to be parallel to the axis of rotation. It is assumed that
        the axis rotates during the day such that the angle to the sun is
        always as small as possible (this means that it will not rotate at
        constant speed during the day). The angle of the axis relative to
        the ground can be given, or you can ask to calculate the optimal
        angle for your location.

    - inclinedaxisangle (float): Inclination angle for a single inclined axis system. (Optional)

        - Inclination angle or slope

        This is the angle of the PV modules from the horizontal plane, for
        a fixed (non-tracking) mounting.

        For some applications the slope and orientation angles will already
        be known, for instance if the PV modules are to be built into an
        existing roof. However, if you have the possibility to choose the
        slope and/or azimuth (orientation), this application can also
        calculate for you the optimal values for slope and orientation
        (assuming fixed angles for the entire year).

    - inclined_optimum (bool): Calculate optimum angle for a single inclined axis system (1) or not (0). (Optional)

        - Optimize inclination of inclined-axis mounting

        If you click to choose this option, PVGIS will calculate the
        inclination of the inclined rotating axis that the PV modules are
        mounted on which gives the highest energy output for the whole
        year.

    - vertical_axis (bool): Calculate a single vertical axis system (1) or not (0). (Optional)

        - Vertical Axis

        In this type of PV system, the modules are mounted on a moving
        structure with a vertical rotating axis, at an angle. The structure
        rotates around the axis during the day such that the angle to the
        sun is always as small as possible (this means that it will not
        rotate at constant speed during the day). The angle of the modules
        relative to the ground can be given, or you can ask to calculate
        the optimal angle for your location.

    - verticalaxisangle (float): Inclination angle for a single vertical axis system. (Optional)

        - Inclination angle or slope

        This is the angle of the PV modules from the horizontal plane, for
        a fixed (non-tracking) mounting. For some applications the slope
        and orientation angles will already be known, for instance if the
        PV modules are to be built into an existing roof. However, if you
        have the possibility to choose the slope and/or azimuth
        (orientation), this application can also calculate for you the
        optimal values for slope and orientation (assuming fixed angles for
        the entire year).

    - vertical_optimum (bool): Calculate optimum angle for a single vertical axis system (1) or not (0). (Optional)

        - Optimize slope

        If you click to choose this option, PVGIS will calculate the slope
        of the PV modules that gives the highest energy output for the
        whole year. This assumes that the slope angle stays fixed for the
        entire year.

    - twoaxis (bool): Calculate a two-axis tracking system (1) or not (0). (Optional)

        - Two Axis

        In this type of PV system, the modules are mounted on a structure
        that can move the modules in the east-west direction and also tilt
        them at an angle from the ground, so that the modules always point
        at the sun. Note that the calculation still assumes that the
        modules do not concentrate the light directly from the sun, but can
        use all the light falling on the modules, both that coming directly
        from the sun and that coming from the rest of the sky.

    - pvprice (bool): Calculate the PV electricity price (1) or not (0). (Optional)
    - systemcost (float): Total cost of installing the PV system in your currency. (Required if pvprice=1)
        - PV system cost

        Here you should input the total cost of installing the PV system,
        including PV system components (PV modules, mounting, inverters,
        cables, etc.) and installation costs (planning, installation, ...).
        The choice of currency is up to you, the electricity price
        calculated by PVGIS will then be the price per kWh of electricity
        in the same currency you used.

    - interest (float): Interest in %/year. (Required if pvprice=1)

        - Interest rate

        This is the interest rate you pay on any loans needed to finance
        the PV system. This assumes a fixed interest rate on the loan which
        will be paid back in yearly instalments over the lifetime of the
        system.

    - lifetime (int): Expected lifetime of the PV system in years. (Required if pvprice=1)

        - PV system lifetime

        This is the expected lifetime of the PV system in years. This is
        used to calculate the effective electricity cost for the system. If
        the PV system happens to last longer the electricity cost will be
        correspondingly lower.

    - outputformat (str): Output format. Choices: "csv", "basic", "json". (Default: "csv")
    - browser (bool): Setting browser=1 and accessing the service through a
      web browser will save the retrieved data to a file. (Default: 0)

    Additional notes:

    - For the fixed PV system, if the parameter `optimalinclination` is set to `1`,
      the value defined for the `angle` parameter is ignored.
      Similarly, if `optimalangles` is set to 1, values defined for `angle` and `aspect`
      are ignored. In which case the parameter `ptimalinclination` is not required either.

    - For the inclined axis PV system analysis,
      the parameter `inclined_axis` must be selected along with
      either `inclinedaxisangle` or `inclined_optimum`.

    - If the parameter `inclined_optimum` is selected,
      the inclination angle defined in `inclinedaxisangle` is ignored,
      so this parameter would not be necessary.

    - Parameters regarding the vertical axis
      (`vertical_axis`, `vertical_optimum` and `verticalaxisangle`)
      are related in the same way as the parameters used for the inclined axis PV system.

    References
    ----------
    Cite the relevant literature, e.g. [1]_.  You may also cite these
    references in the notes section above.

    .. [1]

    Examples
    --------

    """
    # Fake an output for now! -------------------------------------------------
    path_to_module = os.path.dirname(__file__)
    path_to_test_data = pathlib.Path(path_to_module).parent / "tests" / "data"
    csv_files = path_to_test_data.glob("*.csv")
    for csv_file in csv_files:
        output_csv = csv_to_list_of_dictionaries(csv_file)
        print(output_csv)
    # ------------------------------------------------# Fake an output for now!
    return 0


# @app.command('tracking', no_args_is_help=True, help=":satellite_antenna: Estimate PV power output for a system not connected to the grid")
@app.command(
    "tracking",
    no_args_is_help=True,
    help=f":satellite_antenna: Estimate PV power output for a system not connected to the grid {NOT_IMPLEMENTED}",
)
def estimate_tracking_pv():
    """Estimate the energy production of a tracking PV system connected to the electricity grid

    Performance of tracking PV.  PV modules can be placed on mountings that
    move the PV modules to allow them to follow (track) the movement of the sun
    in the sky. In this way we can increase the amount of sunlight arriving at
    the PV modules. This movement can be made in several different ways. Here
    we give three options:

    - Vertical axis: The modules are mounted on a moving structure with a
      vertical rotating axis, at an angle. The structure rotates around the
      axis during the day such that the angle to the sun is always as small as
      possible (this means that it will not rotate at constant speed during the
      day). The angle of the modules relative to the ground can be given, or
      you can ask to calculate the optimal angle for your location.

    - Inclined axis: The modules are mounted on an structure rotating around an
      axis that forms an angle with the ground and points in the north-south
      direction. The plane of the modules is assumed to be parallel to the axis
      of rotation. It is assumed that the axis rotates during the day such that
      the angle to the sun is always as small as possible (this means that it
      will not rotate at constant speed during the day). The angle of the axis
      relative to the ground can be given, or you can ask to calculate the
      optimal angle for your location.

    - Two-axis tracker: The modules are mounted on a system that can move the
      modules in the east-west direction and also tilt them at an angle from
      the ground, so that the modules always point at the sun. Note that the
      calculation still assumes that the modules do not concentrate the light
      directly from the sun, but can use all the light falling on the modules,
      both that coming directly from the sun and that coming from the rest of
      the sky.
    """
    print(f"{NOT_IMPLEMENTED}")


@app.command(
    "offgrid",
    no_args_is_help=True,
    help=f":battery:  Estimate PV power output for a system not connected to the grid {NOT_IMPLEMENTED}",
)
def estimate_offgrid_pv():
    """Estimate the energy production of a PV system that is not connected to
    the electricity grid but instead relies on battery storage

    Performance of off-grid PV systems. This part of PVGIS calculates the
    performance of PV systems that are not connected to the electricity grid
    but instead rely on battery storage to supply energy when the sun is not
    shining. The calculation uses information about the daily variation in
    electricity consumption for the system to simulate the flow of energy to
    the users and into and out of the battery.
    """
    print(f"{NOT_IMPLEMENTED}")

import typer
from typing_extensions import Annotated
from typing import Optional
from .example_pv_estimation_output import csv_to_list_of_dictionaries
from .example_pv_estimation_output import csv_filename
from rich import print


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"PVGIS core CLI prototype",
)


@app.command('grid')
def estimate_grid_connected_pv(
        longitude: Annotated[float, typer.Argument(help='Longitude value', default=None, min=-180, max=180)],  #lon
        latitude: Annotated[float, typer.Argument(default=None, min=-90, max=90)],  # lat
        peakpower: Annotated[float, typer.Argument(default=None, min=0, max=100000000)],  # peakpower
        loss: Annotated[float, typer.Argument(default=None, min=0, max=100)],  # loss
        radiation_database: Annotated[Optional[str], typer.Argument(default=...)] = 'PVGIS-SARAH2',  # raddatabase
        consider_shadows: Annotated[Optional[bool], typer.Argument(default=True)] = True,  # usehorizon
        horizon_heights: Annotated[Optional[int], typer.Argument(default=...)] = None,  # userhorizon
        pv_techonology: Annotated[Optional[str], typer.Argument(default=None)] = None,  # pvtechchoice
        mounting_type: Annotated[Optional[str], typer.Argument(default='free', help='Type of mounting')] = 'free',  # mountingplace
        fixed: Annotated[Optional[bool], typer.Argument(default=True)] = True,  # fixed
        inclination: Annotated[float, typer.Argument(
            help='Inclination angle from horizontal plane of the fixed PV system',
            default=None, min=0, max=90)] = 0,  # angle
        orientation: Annotated[float, typer.Argument(
            help='Orientation (azimuth) of the fixed PV system: 0=south, 90=west, -90=east',
            default=None, min=0, max=180)] = 0,  # aspect
        optimise_angles: Annotated[Optional[bool], typer.Argument(
            help='Optimise inclination and orientation for a fixed PV system',
            default=True)] = False,  # optimalangles
        optimise_inclination: Annotated[Optional[bool], typer.Argument(
            help='Optimise inclination for a fixed PV system',
            default=True)] = False,  # optimalinclination
        single_axis_system: Annotated[Optional[bool], typer.Argument(
            help='Consider a single axis PV system -- Remove Me and improve single_axis_inclination!',
            default=True)] = False,  # inclined_axis
        single_axis_inclination: Annotated[float, typer.Argument(
            help='Inclination for a single axis PV system',
            default=None, min=0, max=90)] = 0,  # inclinedaxisangle
        optimise_single_axis_inclination: Annotated[Optional[bool], typer.Argument(
            help='Optimise inclination for a single axis PV system',
            default=True)] = False,  # inclined_optimum
        vertical_axis_system: Annotated[Optional[bool], typer.Argument(
            help='Consider a single vertical axis PV system -- Remove Me and improve vertical_axis_inclination!',
            default=True)] = False,  # vertical_axis
        vertical_axis_inclination: Annotated[float, typer.Argument(
            help='Inclination for a single axis PV system',
            default=None, min=0, max=90)] = 0,  # Verticalaxisangle
        optimise_vertical_axis_inclination: Annotated[Optional[bool], typer.Argument(
            help='Optimise inclination for a single vertical axis PV system',
            default=True)] = False,  # vertical_optimum
        two_axis_system: Annotated[Optional[bool], typer.Argument(
            help='Consider a two-axis tracking PV system -- Review Me!',
            default=True)] = False,  # twoaxis
        electricity_price: Annotated[Optional[bool], typer.Argument(
            help='Calculate the PV electricity price (kwh/year) for the system cost in the user requested currency -- Review Me!',
            default=True)] = False,  # pvprice
        cost: Annotated[float, typer.Argument(
            help='Total cost of installing the PV system [custom currency]',
            default=None, min=0, max=100000000)] = 0,  # systemcost
        interest: Annotated[float, typer.Argument(
            help='Interest in %/year',
            default=None, min=0, max=100)] = None,  # interest
        lifetime: Annotated[int, typer.Argument(
            help='Expected lifetime of the PV system in years',
            default=25, min=0, max=100)] = 25,  # lifetime
        output_format: Annotated[Optional[str], typer.Argument(default='csv',
            help='Output format')] = 'csv',  # outputformat
    ):
    """Estimate the energy production of a PV system connected to the electricity grid

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
        
    Notes from manual on PVcalc:

        - Based on the original C/C++ program `rsun_standalone_hourly_opt`

        Original Parameters:

        - lat (float): Latitude in decimal degrees, south is negative. (Required)
        - lon (float): Longitude in decimal degrees, west is negative. (Required)
        - peakpower (float): Nominal power of the PV system in kW. (Required)
        - loss (float): Sum of system losses in percent. (Required)
        - raddatabase (str): Radiation database. (Default: "PVGIS-SARAH2")
        - usehorizon (int): Consider shadows from high horizon (1) or not (0). (Default: 1)
        - userhorizon (list): Height of the horizon at equidistant directions around the point of interest, in degrees.
        -                     Starting at north and moving clockwise. (Optional)
        - pvtechchoice (str): PV technology choice. (Optional)
        - mountingplace (str): Type of mounting of the PV modules. Choices are: "free" or "building". (Default: "free")
        - fixed (bool): Calculate a fixed mounted system (1) or not (0). (Default: 1)
        - angle (float): Inclination angle from horizontal plane of the fixed PV system. (Optional)
        - aspect (float): Orientation (azimuth) angle of the fixed PV system. (Optional)
        - optimalangles (bool): Calculate the optimum inclination and orientation angles (1) or not (0). (Optional)
        - optimalinclination (bool): Calculate the optimum inclination angle (1) or not (0). (Optional)
        - inclined_axis (bool): Calculate a single inclined axis system (1) or not (0). (Optional)
        - inclinedaxisangle (float): Inclination angle for a single inclined axis system. (Optional)
        - inclined_optimum (bool): Calculate optimum angle for a single inclined axis system (1) or not (0). (Optional)
        - vertical_axis (bool): Calculate a single vertical axis system (1) or not (0). (Optional)
        - verticalaxisangle (float): Inclination angle for a single vertical axis system. (Optional)
        - vertical_optimum (bool): Calculate optimum angle for a single vertical axis system (1) or not (0). (Optional)
        - twoaxis (bool): Calculate a two-axis tracking system (1) or not (0). (Optional)
        - pvprice (bool): Calculate the PV electricity price (1) or not (0). (Optional)
        - systemcost (float): Total cost of installing the PV system in your currency. (Required if pvprice=1)
        - interest (float): Interest in %/year. (Required if pvprice=1)
        - lifetime (int): Expected lifetime of the PV system in years. (Required if pvprice=1)
        - outputformat (str): Output format. Choices: "csv", "basic", "json". (Default: "csv")
        - browser (bool): Setting browser=1 and accessing the service through a
          web browser will save the retrieved data to a file. (Default: 0)

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

    Returns:
        str: PV calculation result based on the specified input parameters
    """
    # Function implementation goes here
    # Perform the necessary calculations based on the input parameters
    
    output_csv = csv_to_list_of_dictionaries(csv_filename)
    print(output_csv)
    return 0


@app.command('tracking')
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
    pass


@app.command('offgrid')
def estimate_offgrid_pv():
    """Estimate the energy production of a PV system connected that is not
    connected to the electricity grid but instead relies on battery storage

    Performance of off-grid PV systems. This part of PVGIS calculates the
    performance of PV systems that are not connected to the electricity grid
    but instead rely on battery storage to supply energy when the sun is not
    shining. The calculation uses information about the daily variation in
    electricity consumption for the system to simulate the flow of energy to
    the users and into and out of the battery.
    """
    pass

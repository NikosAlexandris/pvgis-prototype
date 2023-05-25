import typer


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"PVGIS core CLI prototype",
)


@app.command('grid')
def estimate_grid_connected_pv():
    """Estimate the energy production of a PV system connected to the electricity grid

    Performance of grid-connected PV systems. This tool makes it possible to
    estimate the average monthly and yearly energy production of a PV system
    connected to the electricity grid, without battery storage. The calculation
    takes into account the solar radiation, temperature, wind speed and type of
    PV module. The user can choose how the modules are mounted, whether on a
    free-standing rack mounting, or integrated in a building surface. PVGIS can
    also calculate the optimum slope and orientation that maximizes the yearly
    energy production. For sun-tracking mountings, see the separate tool below
    this one.
    """
    pass


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

A_PRIMER_ON_SOLAR_GEOMETRY = """
    The amount of solar irradiance incident on a solar surface at a location
    and a moment in time, depends on the [cyan]Solar Incidence[/cyan] angle.

    To calculcate the critical solar incidence angle, PVGIS requires the
    relative [cyan]Latitude[/cyan] and [cyan]Longitude[/cyan] coordinates of
    the surface in question, the [cyan]Surface Tilt[/cyan] and [cyan]Surface
    Orientation[/cyan] angles, the [cyan]Solar Declination[/cyan] and the
    [cyan]Solar Hour[/cyan] angles both of which are derived from the
    [cyan]Timestamp[/cyan] of interest.

    First in order is the calculation of the position of the Earth in its orbit
    around the sun expressed through the angle [cyan]Fractional Year[/cyan]
    measured in radians based solely on a moent in time (timestamp).

    Second is the [cyan]Equation of Time[/cyan] measured in minutes that
    corrects for the eccentricity of the Earth's orbit and axial tilt.

    The [cyan]Time Offset[/cyan] measured in minutes, incorporates the
    [italic]Equation of Time[/italic] and accounts for the variation of the
    Local Solar Time (LST) within a given time zone due to the longitude
    variations within the time zone.

    Next is the [cyan]True solar time[/cyan], also known as the [cyan]Apparent
    solar time[/cyan] upon which depends the calculation of the [cyan]Solar
    hour angle[/cyan].

    The [cyan]Solar Hour angle[/cyan] measures the Earth's rotation and
    indicates the time of the day relative to the position of the sun. It bases
    on the longitude and timestamp and by definition, the solar hour angle is :

        - 0° at solar noon
        - negative in the morning
        - positive in the afternoon

    The order of dependency is :

    - [cyan]Fractional year[/cyan] ⊂ [cyan]Equation of time[/cyan] ⊂ [cyan]Time offset[/cyan] ⊂ [cyan]True solar time[/cyan] ⊂ [cyan]Solar hour angle[/cyan]
    - Solar declination ⊂ Solar zenith ⊂ Solar altitude ⊂ Solar azimuth

    The [cyan]Solar Declination angle[/cyan], depending on the algorithm,
    requires only the [cyan]Fractional Year[/cyan] or in addition the
    [cyan]Eccentricity correction factor[/cyan] and the [cyan]Perigee
    offset[/cyan]) ⊂ [cyan]Solar declination[/cyan]  [bold]PVIS[/bold]

    The order of dependency is :

    - [cyan]Fractional year[/cyan] ⊂ [cyan]Solar declination[/cyan]  [bold]NOAA[/bold]
    or ([cyan]Fractional year[/cyan], [cyan]Eccentricity correction[/cyan], [cyan]Perigee offset[/cyan]) ⊂ [cyan]Solar declination[/cyan]  [bold]PVIS[/bold]
    """


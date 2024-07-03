A_PRIMER_ON_SOLAR_GEOMETRY = """
    The amount of solar irradiance incident on a solar surface at a location
    and a moment in time, depends on the [blue]Solar Incidence[/blue] angle.

    To calculcate the critical [cyan]Solar Incidence[/cyan] angle, PVGIS requires :
    - the relative [cyan]Latitude[/cyan] and [cyan]Longitude[/cyan] coordinates of the surface in question
    - the [cyan]Surface Orientation[/cyan] and [cyan]Surface Tilt[/cyan] angles
    - the [cyan]Solar Declination[/cyan] and the [cyan]Solar Hour[/cyan] angles
    - a [cyan]Timestamp[/cyan] from which to derive the latter two

    [bold]First in order is[/bold] the calculation of the position of the Earth
    in its orbit around the sun expressed through the angle [cyan]Fractional Year[/cyan]
    measured in radians based on a moment in time (timestamp).

    [bold]Second is the[/bold] [cyan]Equation of Time[/cyan] measured in minutes
    that corrects for the eccentricity of the Earth's orbit and axial tilt.

    [bold]Third is the[/bold] [cyan]Time Offset[/cyan] measured in minutes,
    incorporates the [italic]Equation of Time[/italic] and accounts for
    the variation of the Local Solar Time (LST) within a given time zone
    due to the longitude variations within the time zone.

    [bold]Fourth is the[/bold] [cyan]True solar time[/cyan], also known as
    the [cyan]Apparent solar time[/cyan] upon which depends the calculation of
    the [cyan]Solar hour angle[/cyan].

    [bold]Next is the[/bold] [cyan]Solar Hour angle[/cyan] measures
    the Earth's rotation and indicates the time of the day relative to
    the position of the sun. It bases on the longitude and timestamp and
    by definition, the solar hour angle is :

        - 0° at solar noon
        - negative in the morning
        - positive in the afternoon

    The [underline]order of dependency[/underline] is :

    - [cyan]Fractional year[/cyan] ⊂ [cyan]Equation of time[/cyan] ⊂ [cyan]Time offset[/cyan] ⊂ [cyan]True solar time[/cyan] ⊂ [cyan]Solar hour angle[/cyan]
    - Solar declination ⊂ Solar zenith ⊂ Solar altitude ⊂ Solar azimuth

    The [cyan]Solar Declination[/cyan] angle, depending on the algorithm,
    requires only the [cyan]Fractional Year[/cyan] or in addition the
    [cyan]Eccentricity correction factor[/cyan] and the [cyan]Perigee
    offset[/cyan]) ⊂ [cyan]Solar declination[/cyan].

    The order of dependency is :

    - [cyan]Fractional year[/cyan] ⊂ [cyan]Solar declination[/cyan] ([reverse]NOAA[/reverse])

    or

    - ([cyan]Fractional year[/cyan], [cyan]Eccentricity correction[/cyan], [cyan]Perigee offset[/cyan]) ⊂ [cyan]Solar declination[/cyan] ([reverse]Need Reference Here![/reverse])
    """

A_PRIMER_ON_SOLAR_IRRADIANCE = """
    Solar irradiance is the power per unit area (surface power density)
    received from the Sun in the form of electromagnetic radiation in the
    wavelength range of the measuring instrument. Solar irradiance is measured
    in watts per square metre (W/m2) in SI units. (source: Wikipedia)
"""

A_PRIMER_ON_PHOTOVOLTAIC_PERFORMANCE = """
A key metric for evaluating the overall performance of a photovoltaic (PV)
system is the cumulative [yellow]Energy[/yellow] produced over a time period
(e.g., daily, monthly, or annual). In other words, energy production is an
arbitrary aggregate of the instantaneous power estimations over a time series.

In turn, the instantaneous (effective irradiance, and thereby) power values
reflect the [italic]current[/italic] output of the photovoltaic (PV) system
at each moment in time.

How does PVGIS calculcate photovoltaic power output ?
First, we calculcate the position of the sun in the sky relative to the
positioning of a solar surface. Essentially this boils down to one
trigonometric paramter : the solar incidence angle. This angle depends on the
solar altitude and solar azimuth angles on any given moment in time combined
with the location, the orientation and the tilt of the solar surface itself.
Second, we ..

Analytically, we can break down the algorith as follows:
Let us go through the calculation step-by-step.


Hence, .. :

1. Defina an arbitrary period of time

2. Calculate the solar altitude angle series

> The default algoriths for solar timing, positioning and the definition of the
incidence angle are :

    - `solar_time_model` is set to Milne1921 (see in pvgisprototype.constants: SOLAR_TIME_ALGORITHM_DEFAULT).
        - Calculate the apparent solar time based on the equation of time by Milne 1921

    - `solar_position_model` is set to NOAA's equation for .. (see : SOLAR_POSITION_ALGORITHM_DEFAULT).
    - `solar_incidence_model` is set to Iqbal (see : SolarIncidenceModel.iqbal).

3. Calculate the solar azimuth angle series

> NOAA

4. Derive masks of the position of the sun :

  i. above the horizon and not in shade
  ii. very low sun angles
  iii. below the horizon

5. Calculate the direct horizontal irradiance component for ..

6. Calculate the diffuse and reflected irradiance components for the sun above
the horizon

7. Sum the individual irradiance components to derive the global inclined
irradiance

8. Read time series of the ambient temperature, the wind speed and the spectral factor

9. Derive the conversion efficiency coefficients

10. Estimate the photovoltaic power as the product of the global irradiance and
the efficiency coefficients.

"""

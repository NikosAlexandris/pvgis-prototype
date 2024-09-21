from pvgisprototype.api.position.models import SOLAR_POSITION_ALGORITHM_DEFAULT, SOLAR_TIME_ALGORITHM_DEFAULT, SolarIncidenceModel


A_PRIMER_ON_SOLAR_GEOMETRY = """
    The amount of solar irradiance incident on a solar surface at a location
    and a moment in time, depends on the [blue]Solar Incidence[/blue] angle.

    To calculcate the critical [cyan]Solar Incidence[/cyan] angle, PVGIS requires :
    - the relative [cyan]Latitude[/cyan] and [cyan]Longitude[/cyan] coordinates
      of the surface in question
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

A_PRIMER_ON_PHOTOVOLTAIC_PERFORMANCE = f"""
A key metric for evaluating the overall performance of a photovoltaic (PV)
system is the cumulative [yellow]Energy[/yellow] produced over a time period
(e.g., daily, monthly, or annually). In other words, energy production is an
aggregate of the [italic]instantaneous[/italic] power estimations over a time series.

Instantaneous power values reflect the [italic]current[/italic] output of the PV
system at each moment in time, which in turn depends on the effective irradiance.

[bold]How does PVGIS calculate photovoltaic power output ?[/bold]

First, it calculates [italic]the position of the sun[/italic] relative to the
solar surface over the user requested period of time. This boils down to one
key trigonometric parameter : the [cyan]solar incidence[/cyan] angle. The
incidence angle depends on the [cyan]solar altitude[/cyan] and
[cyan]azimuth[/cyan] angles at any given time, combined with the
[cyan]location[/cyan], [cyan]orientation[/cyan], and [cyan]tilt[/cyan] of the
solar surface.

Second and based on the incidence angle, it estimates the [cyan]direct[/cyan]
and [cyan]diffuse[/cyan] [yellow]irradiance[/yellow] components.


### Step by Step

Analytically the algorithm performs the following steps :

1. Define an arbitrary period of time

   The user selects a time period over which the energy production will be
   evaluated.

2. Calculate the [cyan]solar altitude[/cyan] angle series
   
   - The solar altitude angle is the elevation of the sun above the horizon.

   - The default algorithm for solar time is
     [code]solar_time_model[/code] is set to [code]{SOLAR_TIME_ALGORITHM_DEFAULT}[/code]
     (see: [code]pvgisprototype.constants.SOLAR_TIME_ALGORITHM_DEFAULT[/code]).
     This calculates the apparent solar time based on the Equation of Time (Milne, 1921).

   - The default solar positioning algorithm is
     [code]solar_position_model[/code] is set to [code]{SOLAR_POSITION_ALGORITHM_DEFAULT}[/code]
     (see: [code]pvgisprototype.constants.SOLAR_POSITION_ALGORITHM_DEFAULT[/code]).

   - The default model to calculate the solar incidence angle is
     [code]solar_incidence_model[/code] is set to [code]{SolarIncidenceModel.iqbal}[/code]
     (see: [code]SolarIncidenceModel.iqbal[/code]).

3. Calculate the [cyan]solar azimuth[/cyan] angle series
   
   - The solar azimuth is the compass direction from which the sunlight is
     coming, calculated using the NOAA solar position algorithm.

4. Derive masks for solar position
   
   - Create masks for different solar positions

     i. Above the horizon and not in shade.
     ii. Low sun angles (for example, near sunrise or sunset).
     iii. Below the horizon (nighttime).

5. Calculate the direct horizontal irradiance component
   
   - Compute the direct irradiance component that reaches the PV surface from
     the sun without scattering.

6. Calculate the diffuse and ground-reflected irradiance components
   
   - For times when the sun is above the horizon, calculate the diffuse
     irradiance (scattered light) and reflected irradiance (from nearby
     surfaces).

7. Sum the individual irradiance components
   
   - Combine the direct, diffuse, and reflected components to derive the global
     inclined irradiance on the solar panel.

8. Read time series of ambient conditions
   
   - Input data such as ambient temperature, wind speed, and spectral factors
     are read from time series, which affect panel performance.

9. Derive the conversion efficiency coefficients
   
   - Conversion efficiency is calculated based on the temperature, wind speed,
     and other factors influencing the PV panel's ability to convert irradiance
     into power.

10. Estimate the photovoltaic power output
   
   - Photovoltaic power is estimated as the product of the global inclined
     irradiance and the conversion efficiency coefficients. This gives the
     instantaneous power output, which is then integrated over time to
     calculate the total energy produced.

"""

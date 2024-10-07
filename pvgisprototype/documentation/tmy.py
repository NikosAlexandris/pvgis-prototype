A_PRIMER_ON_TYPICAL_METEOROLOGICAL_YEAR = """
The [bold]Typical Meteorological Year[/bold] is a dataset designed to represent
the most "typical" weather conditions for each month at a specific location. It
is based on historical weather data and is used in solar energy simulations,
building performance studies, and other climate-based analyses.

The default method to construct a TMY follows the [blue]ISO 15927-4[/blue]
standard, although other established methods are available. The primary goal is
to capture typical weather conditions by selecting data from the years that
best represent long-term climatic patterns, especially for [cyan]air
temperature[/cyan], [cyan]relative humidity[/cyan], [cyan]solar
radiation[/cyan], and sometimes [cyan]wind speed[/cyan].

The TMY construction process works as follows:

1. [bold]Calculate daily averages[/bold] for each weather variable (e.g., air
temperature) from hourly values for each year.

2. [bold]Create cumulative distribution functions (CDF)[/bold] for each month to
understand the typical monthly pattern, using the daily values from all years.

3. [bold]Compute the [cyan]Finkelstein–Schafer[/cyan] statistic[/bold] for each month
and variable. This measures how different each year’s data is from the
long-term typical pattern (CDF), by comparing the CDF of each year with the
long-term CDF of all years.

4. [bold]Rank each year for each month[/bold] based on the FS statistic. The year with
the lowest FS value is considered the most typical.

5. [bold]Select the best year for each month[/bold]. Wind speed may also be used to
refine the selection further.

    The best months are selected based on the total ranking and a comparison of
    the monthly wind speed deviations from the long-term mean. These selected
    months are then combined to form a full year (e.g., [italic]January 2015,
    February 2011, March 2017[/italic]), which is the Typical Meteorological
    Year (TMY). Boundary values between months may be interpolated to smooth
    discontinuities.

    Depending on the method used (ISO 15927-4, Sandia, or NREL), additional
    criteria, such as the frequency of extreme conditions, may also influence
    the final selection of months.

"""

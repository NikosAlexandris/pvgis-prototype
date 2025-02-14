"""
This module contains days within the year that have some solar significance.

The `SIGNIFICANT_DAYS` list includes key dates such as solstices, equinoxes,
and points of perihelion and aphelion, among others. These dates are significant
in understanding the Earth's orbit around the Sun and its effects on solar irradiance.

Each date is represented as a tuple,
where the first element is the day of the year,
and the second element is an event or description.

Constants:
    SIGNIFICANT_DAYS (list): A list of tuples representing significant dates.
    Each tuple contains a day of the year and a description of the significant event on that day.
Source : Significant Days of the Year, https://andrewmarsh.com/articles/2019/significant-dates/
"""

SIGNIFICANT_DAYS = [
    (3, "Perihelion"),  # Closest point to sun (147 Mio. km)
    (
        42,
        "1st (Greatest) Minimum Point",
    ),  # Great solar time solstice east (greatest lag of the sun)
    (78, "Vernal Equinox"),  # Vernal Point (NH) / Autumn Point (SH)
    (
        105,
        "1st Zero Point",
    ),  # Simultaneity of time at the zone time determination longitude
    (
        134,
        "1st (Second Greatest) Maximum Point",
    ),  # Small solar time solstice west (second greatest lead of the sun)
    (
        164,
        "2nd Zero Point",
    ),  # Simultaneity of time at the zone time determination longitude
    (171, "Summer Solstice (NH) / Winter Solstice (SH)"),
    (186, "Aphelion"),  # Farthest point from the sun (152 Mio. km)
    (
        207,
        "2nd (Second Greatest) Minimum Point",
    ),  # Small solar time solstice east (second largest lag of the sun)
    (
        244,
        "3rd Zero Point",
    ),  # Simultaneity of time at the zone time determination longitude
    (265, "Autumnal, Equinox"),  # Vernal Point (NH) / Autumn Point (SH)
    (
        307,
        "2nd (Greatest) Maximum Point",
    ),  # Great solar time solstice west (greatest lead of the sun)
    (355, "Winter, Solstice (NH) / Summer Solstice (SH)"),
    (
        359,
        "4th Zero Point",
    ),  # Simultaneity of time at the zone time determination longitude
]

import pytest
import numpy as np
from datetime import datetime
from pvgisprototype.algorithms.jenco.solar_incidence import calculate_solar_incidence_time_series_jenco
from .helpers import generate_timestamps_for_a_year
from pvgisprototype import Longitude
from pvgisprototype import Latitude


test_cases = [
    (
        Longitude(value=0.5, unit='radians'),
        Latitude(value=0.5, unit='radians'),
        0.5,
        0.5,
        'minutes',
        'radians',
    ),
    # Add more test cases here
]

@pytest.mark.parametrize(
    "longitude, latitude, surface_tilt, surface_orientation, time_output_units, angle_output_units",
    test_cases,
)
def test_calculate_solar_incidence_time_series_jenco(
        longitude,
        latitude,
        surface_tilt,
        surface_orientation,
        time_output_units,
        angle_output_units,
        ):
    timestamps = generate_timestamps_for_a_year()
    calculated = calculate_solar_incidence_time_series_jenco(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        time_output_units=time_output_units,
        angle_output_units=angle_output_units,
    )
    assert len(calculated) == len(timestamps)
    assert np.all(calculated >= -np.pi / 2) and np.all(calculated <= np.pi / 2)

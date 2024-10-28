import pytest
from pathlib import Path
import numpy as np
import csv
from pandas import DatetimeIndex

from pvgisprototype.cli.write import (
    write_irradiance_csv,
    write_solar_position_series_csv,
    write_spectral_factor_csv,
    safe_get_value
)


def test_safe_get_value():
    """Test the safe_get_value function."""
    dictionary = {"key": [1, 2, 3]}
    result = safe_get_value(dictionary, "key", 1)
    assert result == 2

    # Test with non-existent key
    result = safe_get_value(dictionary, "non_existent_key", 0, default="NA")
    assert result == "NA"

    # Test with scalar value
    dictionary = {"key": 100}
    result = safe_get_value(dictionary, "key", 0)
    assert result == 100


def test_write_irradiance_csv(tmp_path: Path):
    """Test the write_irradiance_csv function with mock CSV."""
    filename = tmp_path / "irradiance.csv"
    dictionary = {"Irradiance": np.array([1000, 1100, 1200])}
    timestamps = DatetimeIndex(["2024-01-01", "2024-01-02", "2024-01-03"])

    write_irradiance_csv(
        longitude=10,
        latitude=20,
        timestamps=timestamps,
        dictionary=dictionary,
        index=True,
        filename=filename,
    )

    # Verify file contents
    with open(filename, "r") as file:
        reader = csv.reader(file)
        rows = list(reader)
        assert rows[0] == ["Index", "Longitude", "Latitude", "Time", "Irradiance"]
        assert rows[1] == ["0", "10", "20", "2024-01-01 00:00:00", "1000"]


def test_write_solar_position_series_csv(tmp_path: Path):
    """Test the write_solar_position_series_csv function."""
    filename = tmp_path / "solar_position.csv"
    timestamps = DatetimeIndex(["2024-01-01", "2024-01-02", "2024-01-03"])

    table = {
        "model_1": {
            "declination": [23.4, 23.5, 23.6],
            "zenith": [60, 59, 58],
            "azimuth": [180, 185, 190],
        }
    }

    write_solar_position_series_csv(
        longitude=10,
        latitude=20,
        timestamps=timestamps,
        timezone="UTC",
        table=table,
        declination=True,
        zenith=True,
        azimuth=True,
        filename=filename,
    )

    # Verify file contents
    with open(filename, "r") as file:
        reader = csv.reader(file)
        rows = list(reader)
        assert rows[0] == [
            "Longitude",
            "Latitude",
            "Time",
            "Zone",
            "Declination",
            "Zenith",
            "Azimuth",
            "Units"
        ]
        assert rows[1] == ["10.0", "20.0", "2024-01-01 00:00:00", "UTC", "23.4", "60", "180", "°"]


def test_write_spectral_factor_csv(tmp_path: Path):
    """Test the write_spectral_factor_csv function."""
    filename = tmp_path / "spectral_factor.csv"
    timestamps = DatetimeIndex(["2024-01-01", "2024-01-02", "2024-01-03"])
    spectral_factor_dictionary = {
        "model_1": {
            "module_type_1": {"Spectral Factor": [0.95, 0.96, 0.97]},
            "module_type_2": {"Spectral Factor": [0.90, 0.91, 0.92]},
        }
    }

    write_spectral_factor_csv(
        longitude=10,
        latitude=20,
        timestamps=timestamps,
        spectral_factor_dictionary=spectral_factor_dictionary,
        filename=filename,
        index=True,
    )

    # Verify file contents
    with open(filename, "r") as file:
        reader = csv.reader(file)
        rows = list(reader)
        assert rows[0] == [
            "Index", "Longitude", "Latitude", "Time", 
            "module_type_1 (model_1)", "module_type_2 (model_1)"
        ]
        assert rows[1] == ["0", "10", "20", "2024-01-01 00:00:00", "0.95", "0.90"]
        assert rows[2] == ["1", "10", "20", "2024-01-02 00:00:00", "0.96", "0.91"]


@pytest.mark.parametrize(
    "key, index, expected_value",
    [
        ("declination", 1, 23.5),
        ("zenith", 2, 58),
        ("azimuth", 0, 180),
        ("non_existent_key", 0, "NA"),
    ],
)
def test_safe_get_value_param(key, index, expected_value):
    """Parameterized test for safe_get_value."""
    model_result = {
        "declination": [23.4, 23.5, 23.6],
        "zenith": [60, 59, 58],
        "azimuth": [180, 185, 190],
    }

    assert safe_get_value(model_result, key, index) == expected_value

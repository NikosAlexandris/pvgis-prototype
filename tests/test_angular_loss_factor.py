

@pytest.mark.parametrize(
    "solar_altitude, solar_declination, expexted_angular_loss_factor",
    [
        (-1000, 90, 0),  # Negative direct radiation
        (1000, -90, 0),  # Negative solar altitude
        (1000, 90, -30),  # Negative incidence angle
    ]
)
def test_calculate_angular_loss_factor_with_invalid_inputs(solar_altitude, solar_declination, expexted_angular_loss_factor):
    with pytest.raises(ValueError):
        calculate_angular_loss_factor(solar_altitude, solar_declination)


@pytest.mark.parametrize(
    "solar_altitude, solar_declination, expexted_angular_loss_factor",
    # Edge cases 
    [
        (1000, 90, 0),
        (0, 45, 45),  # Direct radiation at 0
        (100, 0, 0),  # Solar altitude & incidence angle at 0 : expected radiation is 0
        (100, 45, 45),  # Solar altitude & incidence angle equal
        (100, 90, 90),  # Solar altitude & incidence angle at 90
        (600, 60, 30), 
        (800, 30, 40),  
        (800, 45, 45),
        (1200, 20, 60),
    ]
)
def test_calculate_angular_loss_factor(solar_altitude, solar_declination, expexted_angular_loss_factor):
    result = calculate_angular_loss_factor(solar_altitude, solar_declination)
    assert result == pytest.approx(expexted_angular_loss_factor)




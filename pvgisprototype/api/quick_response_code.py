from datetime import datetime
from enum import Enum

import numpy
import qrcode
from pandas import DatetimeIndex
from PIL.Image import Image

from pvgisprototype.api.statistics.pandas import (
    calculate_mean_of_series_per_time_unit,
    calculate_sum_and_percentage,
)
from pvgisprototype.core.arrays import create_array
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    FINGERPRINT_COLUMN_NAME,
    GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    IRRADIANCE_UNIT_K,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    POWER_UNIT,
    ROUNDING_PLACES_DEFAULT,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_TILT_COLUMN_NAME,
    SYSTEM_EFFICIENCY_COLUMN_NAME,
)


class QuickResponseCode(str, Enum):
    Base64 = "Base64"
    Image = "Image"
    NoneValue = "None"


def generate_quick_response_code(
    dictionary: dict,
    longitude: float,
    latitude: float,
    elevation: float | None = None,
    surface_orientation: bool = True,
    surface_tilt: bool = True,
    timestamps: DatetimeIndex = DatetimeIndex([datetime.now()]),
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    output_type: QuickResponseCode = QuickResponseCode.Base64,
) -> str | Image | None:
    """
    QUICK_RESPONSE_CODE_MOCKUP = "Position: 45.812 8.628, Elevation: 214,
    Orientation: 180, Tilt: 0, Start: 2005-01-01, End: 2020-12-31, Zone: UTC,
    In-Plane Irradiance: 22735.7㎾/m², PV Power: 17494.6 ㎾, Loss: -5241.1
    ㎾/m², Time of Min: 2005-01-01T00:00, Time of Max: 2006-05-30T11:00, Data
    sources: Irradiance: SARAH2 xxxx, Temperature & Wind Speed: ERA5 xxxx,
    Spectral factor: PVGIS 2013, Power Model: Huld 2011, Positioning: NOAA Solar Geometry Equations, Incidence angle: Iqbal 1992, Fingerprint: e9bed6970bc502ae912bdbaf792ef694e449063d4bb6ccd77ab9621a045cbf26"
    """
    # Get float values from dictionary
    surface_orientation = dictionary.get(SURFACE_ORIENTATION_COLUMN_NAME, "")
    surface_tilt = dictionary.get(SURFACE_TILT_COLUMN_NAME, "")
    # Get the "frequency" from the timestamps
    
    #time_groupings = {
    #    "YE": "Yearly",
    #    "S": "Seasonal",
    #    "ME": "Monthly",
    #    "W": "Weekly",
    #    "D": "Daily",
    #    "3H": "3-Hourly",
    #    "H": "Hourly",
    #}
    
    frequency = timestamps.freqstr
    if timestamps.inferred_freq is None:
        frequency = "H"
    if timestamps.year.unique().size > 1:
        frequency = "YE"
    elif timestamps.month.unique().size > 1:
        frequency = "ME"
    elif timestamps.to_period(frequency).week.unique().size > 1:
        frequency = "W"
    elif timestamps.day.unique().size > 1:
        frequency = "D"
    elif timestamps.hour.unique().size < 24:
        frequency = "H"
    else:
        frequency = "3H"
    # frequency_label = time_groupings[frequency]
    
    # In order to avoid unbound errors we pre-define `_series` objects
    array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "init_method": "zeros",
        "backend": array_backend,
    }  # Borrow shape from timestamps

    # Process series
    inclined_irradiance_series = dictionary.get(
        GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,  create_array(**array_parameters)
    )
    inclined_irradiance_mean = calculate_mean_of_series_per_time_unit(
        inclined_irradiance_series, timestamps=timestamps, frequency=frequency
    )
    photovoltaic_power_without_system_loss_series = dictionary.get(
        PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME, create_array(**array_parameters)
    )
    photovoltaic_power_without_system_loss, _ = calculate_sum_and_percentage(
        photovoltaic_power_without_system_loss_series,
        reference_series=1,
        rounding_places=rounding_places,
        dtype=dtype,
        array_backend=array_backend,
    )
    photovoltaic_power_without_system_loss_mean = (
        calculate_mean_of_series_per_time_unit(
            photovoltaic_power_without_system_loss_series,
            timestamps=timestamps,
            frequency=frequency,
        )
    )
    photovoltaic_power_series = dictionary.get(
        PHOTOVOLTAIC_POWER_COLUMN_NAME, create_array(**array_parameters)
    )
    photovoltaic_power_mean = calculate_mean_of_series_per_time_unit(
        photovoltaic_power_series, timestamps=timestamps, frequency=frequency
    )
    system_efficiency_series = dictionary.get(SYSTEM_EFFICIENCY_COLUMN_NAME, None)
    system_efficiency = numpy.nanmedian(system_efficiency_series).astype(
        dtype
    )  # Just in case we ever get time series of `system_efficiency` !
    #system_efficiency_change = (
    #    photovoltaic_power_without_system_loss * system_efficiency
    #    - photovoltaic_power_without_system_loss
    #)
    system_efficiency_change_mean = calculate_mean_of_series_per_time_unit(
        photovoltaic_power_without_system_loss_mean * system_efficiency
        - photovoltaic_power_without_system_loss_mean,
        timestamps=timestamps,
        frequency=frequency,
    )

    # Build output string
    data = ""
    data += "Lat " + str(round_float_values(latitude, rounding_places)) + ", "
    data += "Lon " + str(round_float_values(longitude, rounding_places)) + ", "
    # data += 'Elevation ' + str(round_float_values(elevation, 0)) + ', '
    data += "Elevation " + str(int(elevation)) + ", "
    if isinstance(surface_orientation, list):
        data += (
            "Orientation "
            + ",".join([str(round_float_values(value, rounding_places)) for value in surface_orientation])
            + ", "
        )
    else:
        data += "Orientation " + str(round_float_values(surface_orientation, rounding_places)) + ", "
    if isinstance(surface_tilt, list):
        data += "Tilt " + ",".join([str(round_float_values(value, rounding_places)) for value in surface_tilt]) + ", "
    else:
        data += "Tilt " + str(round_float_values(surface_tilt, rounding_places)) + ", "
    data += "Start " + str(timestamps[0].strftime("%Y-%m-%d %H:%M")) + ", "
    data += "End " + str(timestamps[-1].strftime("%Y-%m-%d %H:%M")) + ", "
    data += (
        "Irradiance "
        + str(round_float_values(inclined_irradiance_mean, 1))
        + f" {IRRADIANCE_UNIT_K}, "
    )
    data += (
        "Power "
        + str(round_float_values(photovoltaic_power_mean, 1))
        + f" {POWER_UNIT}, "
    )
    data += (
        "Loss "
        + str(round_float_values(system_efficiency_change_mean, 1))
        + f" {IRRADIANCE_UNIT_K}, "
    )
    # data_source_irradiance = str
    # data_source_temperature = str
    # data_source_wind_speed = str
    # model_source_spectral_factor = 'PVGIS 2013'
    # model_photovoltaic_module_performance = 'Huld 2011'
    # algorithm_positioning = 'NOAA'
    # algorithm_incidence = 'Iqbal 1992'
    data += "Fingerprint " + dictionary.get(FINGERPRINT_COLUMN_NAME, None) + ", "

    from pvgisprototype._version import __version__

    data += f"PVGIS v6 ({__version__})"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    if output_type == QuickResponseCode.Image:
        return qr  # needs to .make_image()

    if output_type == QuickResponseCode.Base64:
        import base64
        from io import BytesIO

        buffer = BytesIO()
        image = qr.make_image()
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        return image_base64

    return None

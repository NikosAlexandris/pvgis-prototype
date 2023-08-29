from pvgisprototype.api.parameter_models import BaseCoordinatesModel
from pvgisprototype.api.parameter_models import BaseTimestampModel
from pvgisprototype.api.parameter_models import BaseTimeModel


class CalculateSolarTimeSkyfieldInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
):
    pass


class CalculateSolarDeclinationSkyfieldInputModel(
    BaseTimestampModel,
        ):
    pass


class CalculateSolarPositionSkyfieldInputModel(CalculateSolarTimeSkyfieldInputModel):
    pass


class CalculateSolarAltitudeAzimuthSkyfieldInputModel(CalculateSolarPositionSkyfieldInputModel):
    pass


class CalculateHourAngleSkyfieldInput(CalculateSolarPositionSkyfieldInputModel):
    angle_output_units: float

from pvgisprototype.api.parameter_models import ValidatedInputToDict
from pvgisprototype.api.parameter_models import BaseCoordinatesModel
from pvgisprototype.api.parameter_models import BaseTimestampModel
from pvgisprototype.api.parameter_models import BaseTimeModel


class CalculateSolarTimeSkyfieldInputModel(
    ValidatedInputToDict,
    BaseCoordinatesModel,
    BaseTimeModel,
):
    pass


class CalculateSolarDeclinationSkyfieldInputModel(
    ValidatedInputToDict,
    BaseTimestampModel,
        ):
    pass


class CalculateSolarPositionSkyfieldInputModel(CalculateSolarTimeSkyfieldInputModel):
    pass


class CalculateSolarAltitudeAzimuthSkyfieldInputModel(CalculateSolarPositionSkyfieldInputModel):
    pass


class CalculateHourAngleSkyfieldInput(CalculateSolarPositionSkyfieldInputModel):
    angle_output_units: float

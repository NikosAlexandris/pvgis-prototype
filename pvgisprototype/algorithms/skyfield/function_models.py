from pvgisprototype.validation.parameters import BaseCoordinatesModel
from pvgisprototype.validation.parameters import BaseTimestampModel
from pvgisprototype.validation.parameters import BaseTimeModel


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


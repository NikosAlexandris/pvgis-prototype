from pvgisprototype.validation.models import (
    BaseCoordinatesModel,
    BaseTimeModel,
    BaseTimestampModel,
)


class CalculateSolarTimeSkyfieldInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
):
    pass


class CalculateSolarDeclinationSkyfieldInputModel(
    BaseTimestampModel,
):
    pass


class CalculateSolarPositionSkyfieldInputModel(  # Angle output units are not usefull for solar position
    BaseCoordinatesModel,
    BaseTimestampModel,
):
    pass

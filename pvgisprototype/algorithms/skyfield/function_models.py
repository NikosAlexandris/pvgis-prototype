from pvgisprototype.validation.parameters import BaseCoordinatesModel
from pvgisprototype.validation.parameters import BaseTimestampModel
from pvgisprototype.validation.parameters import BaseTimeModel
# from pvgisprototype.validation.parameters import BaseAngleOutputUnitsModel


class CalculateSolarTimeSkyfieldInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
):
    verbose: int = 0
    verbose: int = 0


class CalculateSolarDeclinationSkyfieldInputModel(
    BaseTimestampModel,
        ):
    pass


class CalculateSolarPositionSkyfieldInputModel(  # Angle output units are not usefull for solar position
    BaseCoordinatesModel,
    BaseTimeModel,
):
    pass

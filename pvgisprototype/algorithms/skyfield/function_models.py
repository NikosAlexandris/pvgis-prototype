from pvgisprototype.validation.pvis_data_classes import BaseCoordinatesModel
from pvgisprototype.validation.pvis_data_classes import BaseTimestampModel
from pvgisprototype.validation.pvis_data_classes import BaseTimeModel


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

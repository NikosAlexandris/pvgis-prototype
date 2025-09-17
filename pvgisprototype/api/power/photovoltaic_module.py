from enum import Enum
from typing import Dict, List

from pvgisprototype.api.power.efficiency_coefficients import (
    EFFICIENCY_MODEL_COEFFICIENTS_CIS,
    EFFICIENCY_MODEL_COEFFICIENTS_CIS_BUILDING_INTEGRATED,
    EFFICIENCY_MODEL_COEFFICIENTS_CdTe,
    EFFICIENCY_MODEL_COEFFICIENTS_CdTe_BUILDING_INTEGRATED,
    EFFICIENCY_MODEL_COEFFICIENTS_cSi,
    EFFICIENCY_MODEL_COEFFICIENTS_cSi_BUILDING_INTEGRATED,
    EFFICIENCY_MODEL_COEFFICIENTS_cSi_BUILDING_INTEGRATED_OLD,
    EFFICIENCY_MODEL_COEFFICIENTS_cSi_OLD,
    EFFICIENCY_MODEL_COEFFICIENTS_cSi_2025,
    EFFICIENCY_MODEL_COEFFICIENTS_cSi_BUILDING_INTEGRATED_2025,
)


class PhotovoltaicModuleType(str, Enum):
    Monofacial = "Mono-Facial"
    Bifacial = "Bi-Facial"


class PhotovoltaicModuleModel(Enum):
    CSI_FREE_STANDING_2025 = "cSi:Free standing 2025"
    CSI_INTEGRATED_2025 = "cSi:Integrated 2025"
    CSI_FREE_STANDING = "cSi:Free standing"
    CSI_INTEGRATED = "cSi:Integrated"
    OLD_CSI_FREE_STANDING = "Old cSi:Free standing"
    OLD_CSI_INTEGRATED = "Old cSi:Integrated"
    CIS_FREE_STANDING = "CIS:Free standing"
    CIS_INTEGRATED = "CIS:Integrated"
    CDTE_FREE_STANDING = "CdTe:Free standing"
    CDTE_INTEGRATED = "CdTe:Integrated"


PHOTOVOLTAIC_MODULE_COEFFICIENTS_MAP: Dict[PhotovoltaicModuleModel, List[float]] = {
    PhotovoltaicModuleModel.CSI_FREE_STANDING_2025: EFFICIENCY_MODEL_COEFFICIENTS_cSi_2025,
    PhotovoltaicModuleModel.CSI_INTEGRATED_2025: EFFICIENCY_MODEL_COEFFICIENTS_cSi_BUILDING_INTEGRATED_2025,
    PhotovoltaicModuleModel.CSI_FREE_STANDING: EFFICIENCY_MODEL_COEFFICIENTS_cSi,
    PhotovoltaicModuleModel.CSI_INTEGRATED: EFFICIENCY_MODEL_COEFFICIENTS_cSi_BUILDING_INTEGRATED,
    PhotovoltaicModuleModel.OLD_CSI_FREE_STANDING: EFFICIENCY_MODEL_COEFFICIENTS_cSi_OLD,
    PhotovoltaicModuleModel.OLD_CSI_INTEGRATED: EFFICIENCY_MODEL_COEFFICIENTS_cSi_BUILDING_INTEGRATED_OLD,
    PhotovoltaicModuleModel.CIS_FREE_STANDING: EFFICIENCY_MODEL_COEFFICIENTS_CIS,
    PhotovoltaicModuleModel.CIS_INTEGRATED: EFFICIENCY_MODEL_COEFFICIENTS_CIS_BUILDING_INTEGRATED,
    PhotovoltaicModuleModel.CDTE_FREE_STANDING: EFFICIENCY_MODEL_COEFFICIENTS_CdTe,
    PhotovoltaicModuleModel.CDTE_INTEGRATED: EFFICIENCY_MODEL_COEFFICIENTS_CdTe_BUILDING_INTEGRATED,
}


def get_coefficients_for_photovoltaic_module(
    photovoltaic_module: PhotovoltaicModuleModel,
) -> List[float]:
    """Retrieve model coefficients based on the selected PhotovoltaicModuleModel Enum."""
    coefficients = PHOTOVOLTAIC_MODULE_COEFFICIENTS_MAP.get(photovoltaic_module, [])
    if len(coefficients) < 7:  # should be at least
        raise ValueError("Insufficient number of model constants!")

    return coefficients

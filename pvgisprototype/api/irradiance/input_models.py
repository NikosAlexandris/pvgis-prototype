from pydantic import BaseModel
from pydantic import confloat
from pydantic import field_validator


class Elevation(BaseModel):
    elevation: confloat(ge=0, le=8848)


class OpticalAirMassInputModel(Elevation):
    # refracted_solar_altitude: confloat(ge=-0.6, le=90.6)
    refracted_solar_altitude: float
    angle_units: str = 'degrees',  # Expected value is 'degrees'
    
    @field_validator('angle_units')
    @classmethod
    def validate_angle_output_units(cls, v):
        valid_units = 'degrees'
        if not v == valid_units:
            raise ValueError(f"angle_units must be {valid_units}")
        return v


class IrradianceInputModel(BaseModel):
    linke_turbidity_factor: confloat(ge=0, le=8)  # help='A measure of atmospheric turbidity',
    optical_air_mass: float
    extraterrestial_irradiance: confloat(ge=1360) = 1360.8 # description="The average solar radiation at the top of the atmosphere ~1360.8 W/m^2 (Kopp, 2011)")

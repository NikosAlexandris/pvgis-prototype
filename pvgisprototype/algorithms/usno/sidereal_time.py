#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
from math import cos, fmod, radians, sin
import numpy as np


def calculate_gmst(julian_date_universal_time, H, use_precise_formula=True):
    """Compute the Greenwich mean sidereal time (GMST)"""
    difference_universal_time_minus_20000101120000 = (
        julian_date_universal_time - 2451545.0
    )
    T = difference_universal_time_minus_20000101120000 / 36525.0
    if use_precise_formula:
        GMST = fmod(
            6.697375
            + 0.065709824279 * difference_universal_time_minus_20000101120000
            + 1.0027379 * H
            + 0.0000258 * T**2,
            24,
        )
    else:
        GMST = fmod(
            18.697375
            + 24.065709824279 * difference_universal_time_minus_20000101120000,
            24,
        )
    return GMST


def calculate_gmst_time_series(julian_date_universal_time, H, use_precise_formula=True):
    """Calculate the Greenwich mean sidereal time (GMST) using NumPy"""
    difference_universal_time_minus_20000101120000 = (
        julian_date_universal_time - 2451545.0
    )
    centuries_since_2000 = difference_universal_time_minus_20000101120000 / 36525.0
    if use_precise_formula:
        GMST = np.mod(
            6.697375
            + 0.065709824279 * difference_universal_time_minus_20000101120000
            + 1.0027379 * H
            + 0.0000258 * centuries_since_2000**2,
            24,
        )
    else:
        GMST = np.mod(
            18.697375
            + 24.065709824279 * difference_universal_time_minus_20000101120000,
            24,
        )
    return GMST


def calculate_eqeq(DTT):
    """Compute the equation of the equinoxes (eqeq)"""
    Omega = 125.04 - 0.052954 * DTT
    L = 280.47 + 0.98565 * DTT
    epsilon = 23.4393 - 0.0000004 * DTT
    delta_psi = -0.000319 * sin(radians(Omega)) - 0.000024 * sin(radians(2 * L))
    eqeq = delta_psi * cos(radians(epsilon))
    return eqeq


def calculate_eqeq_time_series(DTT):
    """Calculate the equation of the equinoxes (eqeq)"""
    Omega = 125.04 - 0.052954 * DTT
    L = 280.47 + 0.98565 * DTT
    epsilon = 23.4393 - 0.0000004 * DTT
    delta_psi = -0.000319 * np.sin(np.radians(Omega)) - 0.000024 * np.sin(
        np.radians(2 * L)
    )
    eqeq = delta_psi * np.cos(np.radians(epsilon))
    return eqeq


def calculate_gast(GMST, eqeq):
    """Compute the Greenwich apparent sidereal time (GAST)"""
    return fmod(GMST + eqeq, 24)


def calculate_gast_time_series(GMST, eqeq):
    """Calculate the Greenwich apparent sidereal time (GAST)"""
    return np.mod(GMST + eqeq, 24)


def calculate_local_sidereal_time(GAST, local_longitude_deg):
    """Compute the local mean or apparent sidereal time"""
    local_longitude_hours = local_longitude_deg / 15.0
    return fmod(GAST + local_longitude_hours, 24)


def calculate_local_sidereal_time_time_series(GAST, local_longitude_deg):
    """Calculate the local mean or apparent sidereal time"""
    local_longitude_hours = local_longitude_deg / 15.0
    return np.mod(GAST + local_longitude_hours, 24)


def calculate_apparent_sidereal_time(
    julian_date_universal_time, H, local_longitude_deg, use_precise_formula=True
):
    """Calculate the apparent sidereal time (GAST)"""
    GMST = calculate_GMST(julian_date_universal_time, H, use_precise_formula)
    DTT = julian_date_universal_time - 2451545.0
    eqeq = calculate_eqeq(DTT)
    GAST = calculate_GAST(GMST, eqeq)
    local_sidereal_time = calculate_local_sidereal_time(GAST, local_longitude_deg)
    return {
        "GMST": GMST,
        "eqeq": eqeq,
        "GAST": GAST,
        "local_sidereal_time": local_sidereal_time,
    }


def calculate_apparent_sidereal_time_time_series(
    julian_date_universal_time, H, local_longitude_deg, use_precise_formula=True
):
    """Calculate the apparent sidereal time"""
    GMST = calculate_GMST_time_series(
        julian_date_universal_time, H, use_precise_formula
    )
    DTT = julian_date_universal_time - 2451545.0
    eqeq = calculate_eqeq_time_series(DTT)
    GAST = calculate_GAST_time_series(GMST, eqeq)
    local_sidereal_time = calculate_local_sidereal_time_time_series(
        GAST, local_longitude_deg
    )
    return {
        "GMST": GMST,
        "eqeq": eqeq,
        "GAST": GAST,
        "local_sidereal_time": local_sidereal_time,
    }

from math import radians, tan


def calculate_solar_altitude(zenith):
    """
    Reference for comparison!

    https://github.com/rlxone/SolarNOAA/blob/f044a6ba1ab1e5bdafd0d63d90f134d2192df7f5/Sources/Solar.swift#L286-L308

    Helped me spot the missing 1 degree / 3600 seconds part!
    """
    print(f"Input zenith : {zenith}")
    print(f"Input zenith : {radians(zenith)} in radians")
    exoatmElevation = 90.0 - zenith
    print(f"Input elevation : {exoatmElevation}")
    print(f"Input elevation : {radians(exoatmElevation)} radians")

    if exoatmElevation > 85.0:
        refractionCorrection = 0.0

    else:
        te = tan(radians(exoatmElevation))
        print(f"te : {te}")
        if exoatmElevation > 5.0:
            print(f"Elevation {exoatmElevation} above 5 degrees")
            refractionCorrection = 58.1 / te - 0.07 / pow(te, 3) + 0.000086 / pow(te, 5)
            print(f"refraction is now: {refractionCorrection}")

        elif exoatmElevation > -0.575:
            print(f"Elevation {exoatmElevation} above -0.575 degrees")
            step1 = -12.79 + exoatmElevation * 0.711
            step2 = 103.4 + exoatmElevation * step1
            step3 = -518.2 + exoatmElevation * step2
            refractionCorrection = 1735.0 + exoatmElevation * step3
            print(f"refraction is now: {refractionCorrection}")

        else:
            print(f"Elevation {exoatmElevation} is low")
            refractionCorrection = -20.774 / te
            print(f"refraction is now: {refractionCorrection}")

        refractionCorrection /= 3600.0

    print(f"refractionCorrection : {refractionCorrection}")
    solarzen = zenith - refractionCorrection
    print(f"New solar zenith : {zenith} - {refractionCorrection} = {solarzen}")
    print(f"Returning 90 - {solarzen} = {90 - solarzen}")

    return 90.0 - solarzen

from pvgisprototype.algorithms.pvis.constants import ELECTRON_CHARGE


def calculate_average_photon_energy(  # series ?
    global_irradiance_series_up_to_1050,
    photon_flux_density,
    electron_charge = ELECTRON_CHARGE,
):
    """
    The Average Photon Energy (APE) characterises the energetic distribution
    in an irradiance spectrum. It is calculated by dividing the irradiance
    [W/m² or eV/m²/sec] by the photon flux density [number of photons/m²/sec].

    Notes
    -----
    From [1]_ :

        "The average photon energy is a useful parameter for examining spectral
        effects on the performance of amorphous silicon cells. It is strongly
        correlated with the useful fraction, but is a device independent
        parameter that does not require knowledge of the absorption profile of
        a given device.

        It is possible to examine the purely spectral performance of amorphous
        silicon devices after removing temperature effects from the data.
        Single junction devices show a linear increase in corrected ISC/Gtotal
        as the received radiation becomes more blue shifted, as a greater
        proportion of the insolation lies within its absorption window.
        
        Double and triple junction devices do not vary linearly. The devices
        investigated here reach maxima at 1.72 and 1.7 eV, respectively. As the
        received spectrum becomes either red or blue shifted from this ideal,
        performance drops off due to mismatch between the absorption profile
        and the received spectrum. The output of multijunction devices is
        essentially limited by the layer generating the least current. The
        performance of triple junction cells is more susceptible to changes in
        the incident spectrum than double junction cells, although this will be
        countermanded with lower degradation in the case of a-Si devices.
        
        The maximum spectral performance of multijunction devices occurs at
        APEs higher than the APE where most energy is received. There is an
        opportunity to improve the spectral performance of multijunction
        devices such that they are most efficient at APEs where the majority of
        the energy is delivered.

    References
    ----------
    .. [1] Jardine, C.N. & Gottschalg, Ralph & Betts, Thomas & Infield, David.
      (2002). Influence of Spectral Effects on the Performance of Multijunction
      Amorphous Silicon Cells. to be published.
    """
    # name it series ?
    average_photon_energy = (
        global_irradiance_series_up_to_1050 / photon_flux_density * electron_charge
    )

    return average_photon_energy  # series

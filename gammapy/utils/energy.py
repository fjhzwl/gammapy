# Licensed under a 3-clause BSD style license - see LICENSE.rst
import logging
import numpy as np
from astropy import units as u

__all__ = ["energy_logspace"]

log = logging.getLogger(__name__)


def energy_logspace(emin, emax, nbins, unit=None, per_decade=False):
    """Create Energy with equal log-spacing (`~gammapy.utils.energy.Energy`).

    Parameters
    ----------
    emin : `~astropy.units.Quantity`, float
        Lowest energy bin
    emax : `~astropy.units.Quantity`, float
        Highest energy bin
    nbins : int
        Number of bins
    unit : `~astropy.units.UnitBase`, str
        Energy unit
    per_decade : bool
        Whether nbins is per decade.
    """
    if unit is not None:
        emin = u.Quantity(emin, unit)
        emax = u.Quantity(emax, unit)
    else:
        emin = u.Quantity(emin)
        emax = u.Quantity(emax)
        unit = emax.unit
        emin = emin.to(unit)

    x_min, x_max = np.log10([emin.value, emax.value])

    if per_decade:
        nbins = (x_max - x_min) * nbins

    energy = np.logspace(x_min, x_max, nbins)

    return u.Quantity(energy, unit, copy=False)

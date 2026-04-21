"""
This module defines the parameters of a tyre.
"""

from pydantic import PositiveFloat

from usmlap.filepath import LIBRARY_ROOT
from usmlap.utils.library import HasLibrary


class Tyre(HasLibrary, path=LIBRARY_ROOT / "components" / "tyres"):
    """
    A racing tyre.

    Attributes:
        print_name (str): Printable name of the tyre.
        unloaded_radius (float): The unloaded radius of the tyre.
        tyre_model (TyreModel): The tyre model.
    """

    print_name: str
    effective_radius: float
    mu_x_peak: PositiveFloat
    mu_x_sens: float
    mu_y_peak: PositiveFloat
    mu_y_sens: float
    slip_stiffness: float
    cornering_stiffness: float

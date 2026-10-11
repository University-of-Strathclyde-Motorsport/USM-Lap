"""
This module defines the parameters of a tyre."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, PositiveFloat

from usmlap.core.filepath import LIBRARY_ROOT
from usmlap.core.library import Serialisable


class Tyre(Serialisable, library=LIBRARY_ROOT / "components" / "tyres"):
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


class Tyres(BaseModel):
    """Front and rear tyres."""

    front: Annotated[Tyre, BeforeValidator(Tyre.initialise)]
    rear: Annotated[Tyre, BeforeValidator(Tyre.initialise)]

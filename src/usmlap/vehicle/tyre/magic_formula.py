"""
This module implements the Pacejka Magic Formula tyre model.

Equations are taken from Chapter 4.3.2
of Tire and Vehicle Dynamics (3rd Edition) by Hans Pacejka,
and numbered accordingly.
https://www.sciencedirect.com/book/9780080970165/tire-and-vehicle-dynamics

These equations are in accordance
with the MF-Tire/MF-Swift 6.1.2 Equation Manual,
or MF612 for short.

The following repositories have been used as a starting point for this module:

- Tire Dynamics (Python):
    https://github.com/JyNing04/Pacejka-tire-model/tree/main

- Magic Formula Tyre Library (MATLAB):
    https://github.com/teasit/magic-formula-tyre-library/tree/main
"""

from math import atan, cos, exp, pi, pow, sin, sqrt, tan

from numpy import sign
from pydantic import BaseModel

from usmlap.utils.datatypes import Coordinate

from .tir import TIRParameters

EPSILON = 0.1


class TyreAttitude(BaseModel):
    """
    Parameters describing the attitude of a tyre.

    Attributes:
        Vx:
            Longitudinal velocity of wheel centre.
        Vc:
            Velocity of the wheel contact patch.
        Vs:
            Slip velocity.
        fz:
            Normal load on the tyre.
        omega:
            Wheel speed of revolution.
        kappa:
            Longitudinal slip.
        alpha:
            Side slip angle.
        gamma:
            Camber angle.
        pressure:
            Inflation pressure.
    """

    Vx: float
    Vc: Coordinate
    Vs: Coordinate
    fz: float
    omega: float
    kappa: float
    alpha: float
    gamma: float
    pressure: float


class MagicFormula(object):
    """
    Contains the Pacejka Magic Formula equations.

    Attributes:
        parameters (TIRParameters):
            Tyre parameters loaded from a .TIR file.
        AMU (float):
            Constant used in calculation of digressive friction factor.
        LMUV (float):
            Scaling factor with slip speed vs decaying friction.
    """

    def __init__(self, parameters: TIRParameters, tyre: TyreAttitude) -> None:
        self.parameters = parameters
        self.tyre = tyre
        self.AMU = 1  # Used in calculation of digressive friction factor.
        self.LMUV = 0  # Scaling factor with slip speed vs decaying friction.
        self.use_alpha_star = True

    @property
    def Fz(self) -> float:  # noqa: S100
        return self.Fz

    @property
    def R0(self) -> float:  # noqa: S100
        return self.parameters.DIMENSION.UNLOADED_RADIUS

    @property
    def pressure_ratio(self) -> float:
        return self.tyre.pressure / self.parameters.OPERATING_CONDITIONS.NOMPRES

    @property  # (4.E1)
    def Fz0_prime(self) -> float:  # noqa: S100
        nominal_load = self.parameters.VERTICAL.FNOMIN
        nominal_load_scaling_factor = self.parameters.SCALING_COEFFICIENTS.LFZO
        return nominal_load_scaling_factor * nominal_load

    @property  # (4.E2a)
    def dfz(self) -> float:
        return (self.Fz / self.Fz0_prime) - 1

    @property  # (4.E2b)
    def dpi(self) -> float:
        return self.pressure_ratio - 1

    @property  # (4.E3)
    def alpha(self) -> float:
        if self.use_alpha_star:
            return tan(self.tyre.alpha) * sign(self.tyre.Vc.x)
        else:
            return self.tyre.alpha

    @property  # (4.E4)
    def gamma(self) -> float:
        return sin(self.tyre.gamma)

    @property  # (4.E5)
    def kappa(self) -> float:
        return self.tyre.kappa

    @property  # (4.E6)
    def cos_a(self) -> float:
        return self.tyre.Vc.x / (self.tyre.Vc.norm() + EPSILON)

    @property  # (4.E7a)
    def lmux_star(self) -> float:  # With LMUV = 0, LMU* = LMU
        return self.parameters.SCALING_COEFFICIENTS.LMUX

    @property  # (4.E7b)
    def lmuy_star(self) -> float:  # With LMUV = 0, LMU* = LMU
        return self.parameters.SCALING_COEFFICIENTS.LMUY

    # Helper function for (4.E8)
    def digressive_friction_factor(self, lmu_star: float) -> float:
        return self.AMU * lmu_star / (1 + (self.AMU - 1) * lmu_star)

    @property  # (4.E8a)
    def lmux_prime(self) -> float:
        return self.digressive_friction_factor(self.lmux_star)

    @property  # (4.E8b)
    def lmuy_prime(self) -> float:
        return self.digressive_friction_factor(self.lmuy_star)

    @property  # (4.E9)
    def Fx0(self) -> float:  # noqa: S100
        return self.magic_formula(
            self.Bx, self.Cx, self.Dx, self.Ex, self.kx, self.SVx
        )

    @property  # (4.E10)
    def kx(self) -> float:
        return self.kappa + self.SHx

    @property  # (4.E11)
    def Cx(self) -> float:  # noqa: S100
        PCX1 = self.parameters.LONGITUDINAL_COEFFICIENTS.PCX1
        LCX = self.parameters.SCALING_COEFFICIENTS.LCX
        return PCX1 * LCX

    @property  # (4.E12)
    def Dx(self) -> float:  # noqa: S100
        return self.mux * self.Fz

    @property  # (4.E13)
    def mux(self) -> float:
        PDX1 = self.parameters.LONGITUDINAL_COEFFICIENTS.PDX1
        PDX2 = self.parameters.LONGITUDINAL_COEFFICIENTS.PDX2
        PPX3 = self.parameters.LONGITUDINAL_COEFFICIENTS.PPX3
        PPX4 = self.parameters.LONGITUDINAL_COEFFICIENTS.PPX4
        PDX3 = self.parameters.LONGITUDINAL_COEFFICIENTS.PDX3
        load_factor = PDX1 + PDX2 * self.dfz
        pressure_factor = 1 + PPX3 * self.dpi + PPX4 * self.dpi**2
        camber_factor = 1 - PDX3 * self.tyre.gamma**2
        return load_factor * pressure_factor * camber_factor * self.lmux_star

    @property  # (4.E14)
    def Ex(self) -> float:  # noqa: S100
        PEX1 = self.parameters.LONGITUDINAL_COEFFICIENTS.PEX1
        PEX2 = self.parameters.LONGITUDINAL_COEFFICIENTS.PEX2
        PEX3 = self.parameters.LONGITUDINAL_COEFFICIENTS.PEX3
        PEX4 = self.parameters.LONGITUDINAL_COEFFICIENTS.PEX4
        LEX = self.parameters.SCALING_COEFFICIENTS.LEX
        load_factor = PEX1 + PEX2 * self.dfz + PEX3 * self.dfz**2
        slip_factor = 1 - PEX4 * sign(self.kx)
        return load_factor * slip_factor * LEX

    @property  # (4.E15)
    def Kxk(self) -> float:  # noqa: S100
        PKX1 = self.parameters.LONGITUDINAL_COEFFICIENTS.PKX1
        PKX2 = self.parameters.LONGITUDINAL_COEFFICIENTS.PKX2
        PKX3 = self.parameters.LONGITUDINAL_COEFFICIENTS.PKX3
        PPX1 = self.parameters.LONGITUDINAL_COEFFICIENTS.PPX1
        PPX2 = self.parameters.LONGITUDINAL_COEFFICIENTS.PPX2
        load_factor = self.Fz * (PKX1 + PKX2 * self.dfz) * exp(PKX3 * self.dfz)
        pressure_factor = 1 + PPX1 * self.dpi + PPX2 * self.dpi**2
        return load_factor * pressure_factor

    @property  # (4.E16)
    def Bx(self) -> float:  # noqa: S100
        return self.Kxk / (self.Cx * self.Dx + EPSILON)

    @property  # (4.E17)
    def SHx(self) -> float:  # noqa: S100
        PHX1 = self.parameters.LONGITUDINAL_COEFFICIENTS.PHX1
        PHX2 = self.parameters.LONGITUDINAL_COEFFICIENTS.PHX2
        LHX = self.parameters.SCALING_COEFFICIENTS.LHX
        return (PHX1 + PHX2 * self.dfz) * LHX

    @property  # (4.E18)
    def SVx(self) -> float:  # noqa: S100
        PVX1 = self.parameters.LONGITUDINAL_COEFFICIENTS.PVX1
        PVX2 = self.parameters.LONGITUDINAL_COEFFICIENTS.PVX2
        LVX = self.parameters.SCALING_COEFFICIENTS.LVX
        return self.Fz * (PVX1 + PVX2 * self.dfz) * LVX * self.lmux_prime

    @property  # (4.E19)
    def Fy0(self) -> float:  # noqa: S100
        return self.magic_formula(
            self.By, self.Cy, self.Dy, self.Ey, self.alpha_y, self.SVy
        )

    @property  # (4.E20)
    def alpha_y(self) -> float:
        return self.alpha + self.SHy

    @property  # (4.E21)
    def Cy(self) -> float:  # noqa: S100
        PCY1 = self.parameters.LATERAL_COEFFICIENTS.PCY1
        LCY = self.parameters.SCALING_COEFFICIENTS.LCY
        return PCY1 * LCY

    @property  # (4.E22)
    def Dy(self) -> float:  # noqa: S100
        return self.muy * self.Fz

    @property  # (4.E23)
    def muy(self) -> float:
        PDY1 = self.parameters.LATERAL_COEFFICIENTS.PDY1
        PDY2 = self.parameters.LATERAL_COEFFICIENTS.PDY2
        PPY3 = self.parameters.LATERAL_COEFFICIENTS.PPY3
        PPY4 = self.parameters.LATERAL_COEFFICIENTS.PPY4
        PDY3 = self.parameters.LATERAL_COEFFICIENTS.PDY3
        load_factor = PDY1 + PDY2 * self.dfz
        pressure_factor = 1 + PPY3 * self.dpi + PPY4 * self.dpi**2
        camber_factor = 1 - PDY3 * self.gamma**2
        return load_factor * pressure_factor * camber_factor * self.lmuy_star

    @property  # (4.E24)
    def Ey(self) -> float:  # noqa: S100
        PEY1 = self.parameters.LATERAL_COEFFICIENTS.PEY1
        PEY2 = self.parameters.LATERAL_COEFFICIENTS.PEY2
        PEY3 = self.parameters.LATERAL_COEFFICIENTS.PEY3
        PEY4 = self.parameters.LATERAL_COEFFICIENTS.PEY4
        PEY5 = self.parameters.LATERAL_COEFFICIENTS.PEY5
        LEY = self.parameters.SCALING_COEFFICIENTS.LEY
        load_factor = PEY1 + PEY2 * self.dfz
        camber_term = (PEY3 + PEY4 * self.gamma) * sign(self.alpha_y)
        return load_factor * (1 - camber_term + PEY5 * self.gamma**2) * LEY

    @property  # (4.E25)
    def Kya(self) -> float:  # noqa: S100
        PKY1 = self.parameters.LATERAL_COEFFICIENTS.PKY1
        PKY2 = self.parameters.LATERAL_COEFFICIENTS.PKY2
        PKY3 = self.parameters.LATERAL_COEFFICIENTS.PKY3
        PKY4 = self.parameters.LATERAL_COEFFICIENTS.PKY4
        PKY5 = self.parameters.LATERAL_COEFFICIENTS.PKY5
        PPY1 = self.parameters.LATERAL_COEFFICIENTS.PPY1
        PPY2 = self.parameters.LATERAL_COEFFICIENTS.PPY2
        LKY = self.parameters.SCALING_COEFFICIENTS.LKY
        load_factor = PKY1 * self.Fz0_prime
        pressure_factor = 1 + PPY1 * self.dpi
        camber_factor = 1 - PKY3 * abs(self.gamma)
        adapted_load_ratio = self.Fz / self.Fz0_prime
        factor_K = (PKY2 + PKY5 * self.gamma**2) * (1 + PPY2 * self.dpi)
        sine_factor = sin(PKY4 * atan(adapted_load_ratio / factor_K))
        return load_factor * pressure_factor * camber_factor * sine_factor * LKY

    @property  # (4.E26)
    def By(self) -> float:  # noqa: S100
        return self.Kya / (self.Cy * self.Dy + EPSILON)

    @property  # (4.E27)
    def SHy(self) -> float:  # noqa: S100
        PHY1 = self.parameters.LATERAL_COEFFICIENTS.PHY1
        PHY2 = self.parameters.LATERAL_COEFFICIENTS.PHY2
        LHY = self.parameters.SCALING_COEFFICIENTS.LHY
        nominal_shift = (PHY1 + PHY2 * self.dfz) * LHY
        stiffness_factor = self.Kya + EPSILON
        camber_shift = (self.Kyc0 * self.gamma - self.SVyc) / stiffness_factor
        return nominal_shift + camber_shift

    @property  # (4.E28)
    def SVyc(self) -> float:  # noqa: S100
        PVY3 = self.parameters.LATERAL_COEFFICIENTS.PVY3
        PVY4 = self.parameters.LATERAL_COEFFICIENTS.PVY4
        LKYC = self.parameters.SCALING_COEFFICIENTS.LKYC
        load_factor = self.Fz * (PVY3 + PVY4 * self.dfz)
        return load_factor * self.gamma * LKYC * self.lmuy_prime

    @property  # (4.E29)
    def SVy(self) -> float:  # noqa: S100
        PVY1 = self.parameters.LATERAL_COEFFICIENTS.PVY1
        PVY2 = self.parameters.LATERAL_COEFFICIENTS.PVY2
        LVY = self.parameters.SCALING_COEFFICIENTS.LVY
        load_factor = self.Fz * (PVY1 + PVY2 * self.dfz)
        return load_factor * LVY * self.lmuy_prime + self.SVyc

    @property  # (4.E30)
    def Kyc0(self) -> float:  # noqa: S100
        PKY6 = self.parameters.LATERAL_COEFFICIENTS.PKY6
        PKY7 = self.parameters.LATERAL_COEFFICIENTS.PKY7
        PPY5 = self.parameters.LATERAL_COEFFICIENTS.PKY5
        LKYC = self.parameters.SCALING_COEFFICIENTS.LKYC
        return self.Fz * (PKY6 + PKY7 * self.dfz) * (1 + PPY5 * self.dpi) * LKYC

    @property  # (4.E31)
    def Mz0(self) -> float:  # noqa: S100
        return self.Mz0_prime + self.Mzr0

    @property  # (4.E32)
    def Mz0_prime(self) -> float:  # noqa: S100
        return -self.t0 * self.Fy0

    @property  # (4.E33)
    def t0(self) -> float:
        magic_factor = self.magic_formula(
            self.Bt, self.Ct, self.Dt, self.Et, self.a_t, 0
        )
        return magic_factor * self.cos_a

    @property  # (4.E34)
    def a_t(self) -> float:
        return self.alpha + self.SHt

    @property  # (4.E35)
    def SHt(self) -> float:  # noqa: S100
        QHZ1 = self.parameters.ALIGNING_COEFFICIENTS.QHZ1
        QHZ2 = self.parameters.ALIGNING_COEFFICIENTS.QHZ2
        QHZ3 = self.parameters.ALIGNING_COEFFICIENTS.QHZ3
        QHZ4 = self.parameters.ALIGNING_COEFFICIENTS.QHZ4
        return QHZ1 + QHZ2 * self.dfz + (QHZ3 + QHZ4 * self.dfz) * self.gamma

    @property  # (4.E36)
    def Mzr0(self) -> float:  # noqa: S100
        magic_factor = self.magic_formula_cosine(
            self.Br, self.Cr, self.Dr, 0, self.a_r
        )
        return magic_factor * self.cos_a

    @property  # (4.E37)
    def a_r(self) -> float:
        return self.alpha + self.SHf

    @property  # (4.E38)
    def SHf(self) -> float:  # noqa: S100
        return self.SHy + self.SVy / (self.Kya + EPSILON)

    @property  # (4.E40)
    def Bt(self) -> float:  # noqa: S100
        # Note: QBZ6 is used in place of QBZ4 in Pacejka's book.
        # However, the 6.1.2 manual uses QBZ4.
        # The available tyre data also uses QBZ4, not QBZ6.
        QBZ1 = self.parameters.ALIGNING_COEFFICIENTS.QBZ1
        QBZ2 = self.parameters.ALIGNING_COEFFICIENTS.QBZ2
        QBZ3 = self.parameters.ALIGNING_COEFFICIENTS.QBZ3
        QBZ4 = self.parameters.ALIGNING_COEFFICIENTS.QBZ4
        QBZ5 = self.parameters.ALIGNING_COEFFICIENTS.QBZ5
        LKY = self.parameters.SCALING_COEFFICIENTS.LKY
        load_factor = QBZ1 + QBZ2 * self.dfz + QBZ3 * self.dfz**2
        camber_factor = 1 + QBZ4 * self.gamma + QBZ5 * abs(self.gamma)
        return load_factor * camber_factor * LKY / self.lmuy_prime

    @property  # (4.E41)
    def Ct(self) -> float:  # noqa: S100
        return self.parameters.ALIGNING_COEFFICIENTS.QCZ1

    @property  # (4.E42)
    def Dt0(self) -> float:  # noqa: S100
        QDZ1 = self.parameters.ALIGNING_COEFFICIENTS.QDZ1
        QDZ2 = self.parameters.ALIGNING_COEFFICIENTS.QDZ2
        PPZ1 = self.parameters.ALIGNING_COEFFICIENTS.PPZ1
        LTR = self.parameters.SCALING_COEFFICIENTS.LTR
        load_factor = (self.R0 / self.Fz0_prime) * (QDZ1 + QDZ2 * self.dfz)
        pressure_factor = 1 - PPZ1 * self.dpi
        return self.Fz * load_factor * pressure_factor * LTR

    @property  # (4.E43)
    def Dt(self) -> float:  # noqa: S100
        QDZ3 = self.parameters.ALIGNING_COEFFICIENTS.QDZ3
        QDZ4 = self.parameters.ALIGNING_COEFFICIENTS.QDZ4
        return self.Dt0 * (1 + QDZ3 * abs(self.gamma) + QDZ4 * self.gamma**2)

    @property  # (4.E44)
    def Et(self) -> float:  # noqa: S100
        QEZ1 = self.parameters.ALIGNING_COEFFICIENTS.QEZ1
        QEZ2 = self.parameters.ALIGNING_COEFFICIENTS.QEZ2
        QEZ3 = self.parameters.ALIGNING_COEFFICIENTS.QEZ3
        QEZ4 = self.parameters.ALIGNING_COEFFICIENTS.QEZ4
        QEZ5 = self.parameters.ALIGNING_COEFFICIENTS.QEZ5
        load_factor = QEZ1 + QEZ2 * self.dfz + QEZ3 * self.dfz**2
        camber_factor = QEZ4 + QEZ5 * self.gamma
        shape_factor = (2 / pi) * atan(self.Bt * self.Ct * self.a_t)
        return load_factor * (1 + camber_factor * shape_factor)

    @property  # (4.E45)
    def Br(self) -> float:  # noqa: S100
        QBZ9 = self.parameters.ALIGNING_COEFFICIENTS.QBZ9
        QBZ10 = self.parameters.ALIGNING_COEFFICIENTS.QBZ10
        LKY = self.parameters.SCALING_COEFFICIENTS.LKY
        return QBZ9 * LKY / self.lmuy_star + QBZ10 * self.By * self.Cy

    @property  # (4.E46)
    def Cr(self) -> float:  # noqa: S100
        return 1

    @property  # (4.E47)
    def Dr(self) -> float:  # noqa: S100
        align = self.parameters.ALIGNING_COEFFICIENTS
        LRES = self.parameters.SCALING_COEFFICIENTS.LRES
        LKZC = self.parameters.SCALING_COEFFICIENTS.LKZC
        load_factor = (align.QDZ6 + align.QDZ7 * self.dfz) * LRES
        pressure_load_factor = align.QDZ8 + align.QDZ9 * self.dfz
        pressure_factor = pressure_load_factor * (1 + align.PPZ2 * self.dpi)
        camber_load_sensivitity = align.QDZ10 + align.QDZ11 * self.dfz
        camber_sensitivity = camber_load_sensivitity * abs(self.gamma)
        camber_factor = load_factor + (pressure_factor + camber_sensitivity)
        camber_influence = camber_factor * self.gamma * LKZC * self.lmuy_star
        direction = sign(self.tyre.Vc.x)
        return self.Fz * self.R0 * camber_influence * direction * self.cos_a

    @property  # (4.E50)
    def Fx(self) -> float:  # noqa: S100
        return self.Gxa * self.Fx0

    @property  # (4.E51)
    def Gxa(self) -> float:  # noqa: S100
        magic_factor = self.magic_formula_cosine(
            self.Bxa, self.Cxa, 1, self.Exa, self.alpha_s
        )
        return magic_factor / self.Gxa0

    @property  # (4.E52)
    def Gxa0(self) -> float:  # noqa: S100
        return self.magic_formula_cosine(
            self.Bxa, self.Cxa, 1, self.Exa, self.SHxa
        )

    @property  # (4.E53)
    def alpha_s(self) -> float:
        return self.alpha + self.SHxa

    @property  # (4.E54)
    def Bxa(self) -> float:  # noqa: S100
        RBX1 = self.parameters.LONGITUDINAL_COEFFICIENTS.RBX1
        RBX2 = self.parameters.LONGITUDINAL_COEFFICIENTS.RBX2
        RBX3 = self.parameters.LONGITUDINAL_COEFFICIENTS.RBX3
        LXAL = self.parameters.SCALING_COEFFICIENTS.LXAL
        camber_factor = RBX1 + RBX3 * self.gamma**2
        slip_factor = cos(atan(RBX2 * self.kappa))
        return camber_factor * slip_factor * LXAL

    @property  # (4.E55)
    def Cxa(self) -> float:  # noqa: S100
        return self.parameters.LONGITUDINAL_COEFFICIENTS.RCX1

    @property  # (4.E56)
    def Exa(self) -> float:  # noqa: S100
        REX1 = self.parameters.LONGITUDINAL_COEFFICIENTS.REX1
        REX2 = self.parameters.LONGITUDINAL_COEFFICIENTS.REX2
        return REX1 + REX2 * self.dfz

    @property  # (4.E57)
    def SHxa(self) -> float:  # noqa: S100
        return self.parameters.LONGITUDINAL_COEFFICIENTS.RHX1

    @property  # (4.E58)
    def Fy(self) -> float:  # noqa: S100
        return self.Gyk * self.Fy0 + self.SVyk

    @property  # (4.E59)
    def Gyk(self) -> float:  # noqa: S100
        magic_factor = self.magic_formula_cosine(
            self.Byk, self.Cyk, 1, self.Eyk, self.k_s
        )
        return magic_factor / self.Gyk0

    @property  # (4.E60)
    def Gyk0(self) -> float:  # noqa: S100
        return self.magic_formula_cosine(
            self.Byk, self.Cyk, 1, self.Eyk, self.SHyk
        )

    @property  # (4.E61)
    def k_s(self) -> float:
        return self.kappa + self.SHyk

    @property  # (4.E62)
    def Byk(self) -> float:  # noqa: S100
        RBY1 = self.parameters.LATERAL_COEFFICIENTS.RBY1
        RBY2 = self.parameters.LATERAL_COEFFICIENTS.RBY2
        RBY3 = self.parameters.LATERAL_COEFFICIENTS.RBY3
        RBY4 = self.parameters.LATERAL_COEFFICIENTS.RBY4
        LYKA = self.parameters.SCALING_COEFFICIENTS.LYKA
        camber_factor = RBY1 + RBY4 * self.gamma**2
        slip_factor = cos(atan(RBY2 * (self.alpha - RBY3)))
        return camber_factor * slip_factor * LYKA

    @property  # (4.E63)
    def Cyk(self) -> float:  # noqa: S100
        return self.parameters.LATERAL_COEFFICIENTS.RCY1

    @property  # (4.E64)
    def Eyk(self) -> float:  # noqa: S100
        REY1 = self.parameters.LATERAL_COEFFICIENTS.REY1
        REY2 = self.parameters.LATERAL_COEFFICIENTS.REY2
        return REY1 + REY2 * self.dfz

    @property  # (4.E65)
    def SHyk(self) -> float:  # noqa: S100
        RHY1 = self.parameters.LATERAL_COEFFICIENTS.RHY1
        RHY2 = self.parameters.LATERAL_COEFFICIENTS.RHY2
        return RHY1 + RHY2 * self.dfz

    @property  # (4.E66)
    def SVyk(self) -> float:  # noqa: S100
        RVY5 = self.parameters.LATERAL_COEFFICIENTS.RVY5
        RVY6 = self.parameters.LATERAL_COEFFICIENTS.RVY6
        LVYKA = self.parameters.SCALING_COEFFICIENTS.LVYKA
        return self.DVyk * sin(RVY5 * atan(RVY6 * self.kappa)) * LVYKA

    @property  # (4.E67)
    def DVyk(self) -> float:  # noqa: S100
        RVY1 = self.parameters.LATERAL_COEFFICIENTS.RVY1
        RVY2 = self.parameters.LATERAL_COEFFICIENTS.RVY2
        RVY3 = self.parameters.LATERAL_COEFFICIENTS.RVY3
        RVY4 = self.parameters.LATERAL_COEFFICIENTS.RVY4
        load_factor = RVY1 + RVY2 * self.dfz + RVY3 * self.gamma
        slip_factor = cos(atan(RVY4 * self.alpha))
        return self.muy * self.Fz * load_factor * slip_factor

    @property  # (4.E69)
    def Mx(self) -> float:  # noqa: S100
        q = self.parameters.OVERTURNING_COEFFICIENTS
        LVMX = self.parameters.SCALING_COEFFICIENTS.LVMX
        LMX = self.parameters.SCALING_COEFFICIENTS.LMX
        load_ratio = self.Fz / self.parameters.VERTICAL.FNOMIN

        offset = q.QSX1 * LVMX
        pressure_term = q.QSX2 * self.gamma * (1 + q.PPMX1 * self.dpi)
        load_term = q.QSX3 * load_ratio
        cosine_factor = cos(q.QSX5 * atan(q.QSX6 * load_ratio) ** 2)
        arctan_factor = atan(q.QSX9 * load_ratio)
        sine_factor = sin(q.QSX7 * self.gamma + q.QSX8 * arctan_factor)
        trig_term = q.QSX4 * cosine_factor * sine_factor
        camber_term = q.QSX10 * atan(q.QSX11 * load_ratio) * self.gamma
        terms = offset - pressure_term + load_term + trig_term + camber_term
        return self.Fz * self.R0 * terms * LMX

    @property  # (4.E70)
    def My(self) -> float:  # noqa: S100
        q = self.parameters.ROLLING_COEFFICIENTS
        nominal_load = self.parameters.VERTICAL.FNOMIN
        v_ratio = self.tyre.Vx / self.parameters.MODEL.LONGVL
        force_ratio = self.Fz / nominal_load
        LMY = self.parameters.SCALING_COEFFICIENTS.LMY

        longitudinal_term = q.QSY2 * self.Fx / nominal_load
        velocity_term = q.QSY3 * abs(v_ratio) + q.QSY4 * v_ratio**4
        camber_term = (q.QSY5 + q.QSY6 * force_ratio) * (self.tyre.gamma**2)
        factor_a = q.QSY1 + longitudinal_term + velocity_term + camber_term
        factor_b = pow(force_ratio, q.QSY7) * pow(self.pressure_ratio, q.QSY8)
        return self.Fz * self.R0 * factor_a * factor_b * LMY

    @property  # (4.E71)
    def Mz(self) -> float:  # noqa: S100
        return self.Mz_prime + self.Mzr + self.s * self.Fx

    @property  # (4.E72)
    def Mz_prime(self) -> float:  # noqa: S100
        return -self.t * self.Fy_prime

    @property  # (4.E73)
    def t(self) -> float:
        magic_factor = self.magic_formula_cosine(
            self.Bt, self.Ct, self.Dt, self.Et, self.a_teq
        )
        return magic_factor * self.cos_a

    @property  # (4.E74)
    def Fy_prime(self) -> float:  # noqa: S100
        return self.Gyk * self.Fy0

    @property  # (4.E75)
    def Mzr(self) -> float:  # noqa: S100
        magic_factor = self.magic_formula_cosine(
            self.Br, self.Cr, self.Dr, 0, self.a_req
        )
        return magic_factor * self.cos_a

    @property  # (4.E76)
    def s(self) -> float:
        SSZ1 = self.parameters.ALIGNING_COEFFICIENTS.SSZ1
        SSZ2 = self.parameters.ALIGNING_COEFFICIENTS.SSZ2
        SSZ3 = self.parameters.ALIGNING_COEFFICIENTS.SSZ3
        SSZ4 = self.parameters.ALIGNING_COEFFICIENTS.SSZ4
        LS = self.parameters.SCALING_COEFFICIENTS.LS
        load_factor = SSZ2 * self.Fy / self.Fz0_prime
        camber_factor = (SSZ3 + SSZ4 * self.dfz) * self.gamma
        return self.R0 * (SSZ1 + load_factor + camber_factor) * LS

    @property  # Helper function for (4.E77) and (4.E78)
    def _stiffness_factor(self) -> float:
        return self.kappa * self.Kxk / (self.Kya + EPSILON)

    @property  # (4.E77)
    def a_teq(self) -> float:
        return sqrt(self.a_t**2 + self._stiffness_factor**2) * sign(self.a_t)

    @property  # (4.E78)
    def a_req(self) -> float:
        return sqrt(self.a_r**2 + self._stiffness_factor**2) * sign(self.a_r)

    @staticmethod
    def magic_formula(
        B: float, C: float, D: float, E: float, x: float, SV: float
    ) -> float:
        """
        Implements the Pacejka Magic Formula.

        Calculates longitudinal force Fx,
        lateral force Fy, or aligning moment Mz.

        Args:
            B (float): Stiffness factor.
            C (float): Shape factor.
            D (float): Peak value.
            E (float): Curvature factor.
            x (float): Input variable (kappa, alpha, or gamma),
                plus horizontal shift.
            SV (float): Vertical shift.

        Returns:
            Y (float): Output variable (either Fx, Fy, or Mz).
        """
        Bx = B * x
        return D * sin(C * atan(Bx - E * (Bx - atan(Bx)))) + SV

    @staticmethod
    def magic_formula_cosine(
        B: float, C: float, D: float, E: float, x: float
    ) -> float:
        """
        Implements the cosine version of the Pacejka Magic Formula.

        Args:
            B (float): Stiffness factor.
            C (float): Shape factor.
            D (float): Peak value.
            E (float): Curvature factor.
            x (float): Input variable (kappa, alpha, or gamma),
                plus horizontal shift.

        Returns:
            Y (float): Output variable.
        """
        Bx = B * x
        return D * cos(C * atan(Bx - E * (Bx - atan(Bx))))

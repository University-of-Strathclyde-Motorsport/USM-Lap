"""
This module provides support for reading tyre data from .TIR files.

The .TIR file format specifies a wide range of tyre parameters
which can be used in the Pacejka Magic Formula.

Documentation for the .TIR file format is available at
https://functionbay.com/documentation/onlinehelp/Documents/Tire/MFTyre-MFSwift_Help.pdf,
in section 5.3.
"""

import re
from abc import ABC
from typing import Optional, Self

from pydantic import BaseModel


class _ParameterGroup(ABC, BaseModel):
    """
    Base class for parameter groups.
    """

    pass


class Units(_ParameterGroup):
    """
    Units used in the .TIR file.

    Attributes:
        LENGTH: Length units (default: "meter").
        FORCE: Force units (default: "newton").
        ANGLE: Angle units (default: "radians").
        MASS: Mass units (default: "kg").
        TIME: Time units (default: "second").
    """

    LENGTH: str
    FORCE: str
    ANGLE: str
    MASS: str
    TIME: str


class Model(_ParameterGroup):
    """
    Parameters on the usage of the tyre model.

    Attributes:
        FITTYP (int): Magic Formula version number.
        TYRESIDE (str): Position of tyre during measurements.
            "LEFT" or "RIGHT" (default = "LEFT").
        LONGVL (float): Reference speed.
        VXLOW (float): Lower boundary velocity in slip calculation.
        ROAD_INCREMENT (Optional[float]): Increment in road sampling.
        ROAD_DIRECTION (Optional[float]): Direction of travelled distance.
            1 = default, -1 = reverse (default = 1)
    """

    FITTYP: int
    TYRESIDE: str = "LEFT"
    LONGVL: float
    VXLOW: float
    ROAD_INCREMENT: Optional[float] = None
    ROAD_DIRECTION: Optional[float] = 1


class Dimension(_ParameterGroup):
    """
    Tyre dimensions.

    Attributes:
        UNLOADED_RADIUS (float): Free tyre radius.
        WIDTH (Optional[float]): Nominal section width of the tyre.
        RIM_RADIUS (Optional[float]): Nominal rim radius.
        RIM_WIDTH (Optional[float]): Rim width.
        ASPECT_RATIO (Optional[float]): Nominal aspect ratio.
    """

    UNLOADED_RADIUS: float
    WIDTH: Optional[float] = None
    RIM_RADIUS: Optional[float] = None
    RIM_WIDTH: Optional[float] = None
    ASPECT_RATIO: Optional[float] = None


class OperatingConditions(_ParameterGroup):
    """
    Operating conditions of the tyre.

    Attributes:
        INFLPRES (float): Tyre inflation pressure.
        NOMPRES (float): Nominal pressure used in Magic Formula equations.
    """

    INFLPRES: float
    NOMPRES: float


class Inertia(_ParameterGroup):
    """
    Mass and inertia properties of the tyre and tyre belt.

    Attributes:
        MASS (Optional[float]): Tyre mass.
        IXX (Optional[float]): Tyre diametral moment of inertia.
        IYY (Optional[float]): Tyre polar moment of inertia.
        BELT_MASS (Optional[float]): Belt mass.
        BELT_IXX (Optional[float]): Belt diametral moment of inertia.
        BELT_IYY (Optional[float]): Belt polar moment of inertia.
        GRAVITY (Optional[float]): Gravity acting on belt in Z direction.
    """

    MASS: Optional[float] = None
    IXX: Optional[float] = None
    IYY: Optional[float] = None
    BELT_MASS: Optional[float] = None
    BELT_IXX: Optional[float] = None
    BELT_IYY: Optional[float] = None
    GRAVITY: Optional[float] = None


class Vertical(_ParameterGroup):
    """
    Vertical stiffness, loaded and effective rolling radius.

    Attributes:
        FNOMIN (float): Nominal wheel load.
        VERTICAL_STIFFNESS (Optional[float]): tyre vertical stiffness.
        VERTICAL_DAMPING (Optional[float]): tyre vertical damping.
        MC_CONTOUR_A (Optional[float]): Motorcycle contour ellipse A.
        MC_CONTOUR_B (Optional[float]): Motorcycle contour ellipse B.
        BREFF (Optional[float]): Low load stiffness of effective rolling radius.
        DREFF (Optional[float]): Peak value of effective rolling radius.
        FREFF (Optional[float]):
            High load stiffness of effective rolling radius.
        Q_RE0 (Optional[float]):
            Ratio of free tyre radius with nominal tyre radius.
        Q_V1 (Optional[float]): tyre radius increase with speed.
        Q_V2 (Optional[float]): Vertical stiffness increase with speed.
        Q_FZ2 (Optional[float]): Quadratic term in load vs. deflection.
        Q_FCX (Optional[float]):
            Longitudinal force influence on vertical stiffness.
        Q_FCY (Optional[float]): Lateral force influence on vertical stiffness.
        Q_FCY2 (Optional[float]): Explicit load dependency for including
            the lateral force influence on vertical stiffness.
        Q_CAM (Optional[float]): Stiffness reduction due to camber.
        Q_CAM1 (Optional[float]): Linear load dependent camber angle
            influence on vertical stiffness.
        Q_CAM2 (Optional[float]): Quadratic load dependent camber angle
            influence on vertical stiffness.
        Q_CAM3 (Optional[float]): Linear load and camber angle dependent
            reduction on vertical stiffness.
        Q_FYS1 (Optional[float]): Combined camber angle and side slip angle
            effect on vertical stiffness (constant).
        Q_FYS2 (Optional[float]): Combined camber angle and side slip angle
            linear effect on vertical stiffness.
        Q_FYS3 (Optional[float]): Combined camber angle and side slip angle
            quadratic effect on vertical stiffness.
        PFZ1 (Optional[float]): Pressure effect on vertical stiffness.
        BOTTOM_OFFST (Optional[float]):
            Distance to rim when bottoming starts to occur.
        BOTTOM_STIFF (Optional[float]): Vertical stiffness of bottomed tyre.
    """

    FNOMIN: float
    VERTICAL_STIFFNESS: Optional[float] = None
    VERTICAL_DAMPING: Optional[float] = None
    MC_CONTOUR_A: Optional[float] = None
    MC_CONTOUR_B: Optional[float] = None
    BREFF: Optional[float] = None
    DREFF: Optional[float] = None
    FREFF: Optional[float] = None
    Q_RE0: Optional[float] = None
    Q_V1: Optional[float] = None
    Q_V2: Optional[float] = None
    Q_FZ2: Optional[float] = None
    Q_FCX: Optional[float] = None
    Q_FCY: Optional[float] = None
    Q_FCY2: Optional[float] = None
    Q_CAM: Optional[float] = None
    Q_CAM1: Optional[float] = None
    Q_CAM2: Optional[float] = None
    Q_CAM3: Optional[float] = None
    Q_FYS1: Optional[float] = None
    Q_FYS2: Optional[float] = None
    Q_FYS3: Optional[float] = None
    PFZ1: Optional[float] = None
    BOTTOM_OFFST: Optional[float] = None
    BOTTOM_STIFF: Optional[float] = None


class Structural(_ParameterGroup):
    """
    Tyre stiffness, damping, and eigenfrequencies.

    Attributes:
        LONGITUDINAL_STIFFNESS (Optional[float]):
            Tyre overall longitudinal stiffness.
        LATERAL_STIFFNESS (Optional[float]): Tyre overall lateral stiffness.
        YAW_STIFFNESS (Optional[float]): Tyre overall yaw stiffness.
        FREQ_LONG (Optional[float]):
            Undamped frequency fore/aft and vertical mode.
        FREQ_LAT (Optional[float]): Undamped frequency lateral mode.
        FREQ_YAW (Optional[float]): Undamped frequency yaw and camber mode.
        FREQ_WINDUP (Optional[float]): Undamped frequency wind-up mode.
        DAMP_LONG (Optional[float]):
            Dimensionless damping fore/aft and vertical mode.
        DAMP_LAT (Optional[float]): Dimensionless damping lateral mode.
        DAMP_YAW (Optional[float]): Dimensionless damping yaw and camber mode.
        DAMP_WINDUP (Optional[float]): Dimensionless damping wind-up mode.
        DAMP_RESIDUAL (Optional[float]):
            Residual damping (proportional to stiffness).
        DAMP_VLOW (Optional[float]):
            Additional low speed damping (proportional to stiffness).
        Q_BVX (Optional[float]):
            Load and speed influence on in-plane translation stiffness.
        Q_BVT (Optional[float]):
            Load and speed influence on in-plane rotation stiffness.
        PCFX1 (Optional[float]): Tyre overall longitudinal stiffness
            vertical deflection dependency linear term.
        PCFX2 (Optional[float]): Tyre overall longitudinal stiffness
            vertical deflection dependency quadratic term.
        PCFX3 (Optional[float]):
            Tyre overall longitudinal stiffness pressure dependency.
        PCFY1 (Optional[float]): Tyre overall lateral stiffness
            vertical deflection dependency linear term.
        PCFY2 (Optional[float]): Tyre overall lateral stiffness
            vertical deflection dependency quadratic term.
        PCFY3 (Optional[float]):
            Tyre overall lateral stiffness pressure dependency.
        PCMZ1 (Optional[float]): Tyre overall yaw stiffness pressure dependency.
    """

    LONGITUDINAL_STIFFNESS: Optional[float] = None
    LATERAL_STIFFNESS: Optional[float] = None
    YAW_STIFFNESS: Optional[float] = None
    FREQ_LONG: Optional[float] = None
    FREQ_LAT: Optional[float] = None
    FREQ_YAW: Optional[float] = None
    FREQ_WINDUP: Optional[float] = None
    DAMP_LONG: Optional[float] = None
    DAMP_LAT: Optional[float] = None
    DAMP_YAW: Optional[float] = None
    DAMP_WINDUP: Optional[float] = None
    DAMP_RESIDUAL: Optional[float] = None
    DAMP_VLOW: Optional[float] = None
    Q_BVX: Optional[float] = None
    Q_BVT: Optional[float] = None
    PCFX1: Optional[float] = None
    PCFX2: Optional[float] = None
    PCFX3: Optional[float] = None
    PCFY1: Optional[float] = None
    PCFY2: Optional[float] = None
    PCFY3: Optional[float] = None
    PCMZ1: Optional[float] = None


class ContactPatch(_ParameterGroup):
    """
    Contact length and obstacle enveloping parameters.

    Attributes:
        Q_RA1 (Optional[float]): Square root term in contact length equation.
        Q_RA2 (Optional[float]): Linear term in contact length equation.
        Q_RB1 (Optional[float]): Root term in contact width equation.
        Q_RB2 (Optional[float]): Linear term in contact width equation.
        ELLIPS_SHIFT (Optional[float]):
            Scaling of distance between front and rear ellipsoid.
        ELLIPS_LENGTH (Optional[float]): Semimajor axis of ellipsoid.
        ELLIPS_HEIGHT (Optional[float]): Semiminor axis of ellipsoid.
        ELLIPS_ORDER (Optional[float]): Order of ellipsoid.
        ELLIPS_MAX_STEP (Optional[float]): Maximum height of road step.
        ELLIPS_NWIDTH (Optional[float]): Number of parallel ellipsoids.
        ELLIPS_NLENGTH (Optional[float]):
            Number of ellipsoids at sides of contact patch.
        ENV_C1 (Optional[float]): Effective height attenuation.
        ENV_C2 (Optional[float]): Effective plane angle attenuation.
        Q_A2 (Optional[float]): Linear load term in contact length.
        Q_A1 (Optional[float]): Square root load term in contact length.
    """

    Q_RA1: Optional[float] = None
    Q_RA2: Optional[float] = None
    Q_RB1: Optional[float] = None
    Q_RB2: Optional[float] = None
    ELLIPS_SHIFT: Optional[float] = None
    ELLIPS_LENGTH: Optional[float] = None
    ELLIPS_HEIGHT: Optional[float] = None
    ELLIPS_ORDER: Optional[float] = None
    ELLIPS_MAX_STEP: Optional[float] = None
    ELLIPS_NWIDTH: Optional[float] = None
    ELLIPS_NLENGTH: Optional[float] = None
    ENV_C1: Optional[float] = None
    ENV_C2: Optional[float] = None
    Q_A2: Optional[float] = None
    Q_A1: Optional[float] = None


class InflationPressureRange(_ParameterGroup):
    """
    Minimum and maximum allowed inflation pressures.

    Attributes:
        PRESMIN (Optional[float]): Minimum allowed inflation pressure.
        PRESMAX (Optional[float]): Maximum allowed inflation pressure.
    """

    PRESMIN: Optional[float] = None
    PRESMAX: Optional[float] = None


class VerticalForceRange(_ParameterGroup):
    """
    Minimum and maximum allowed wheel loads.

    Attributes:
        FZMIN (Optional[float]): Minimum allowed wheel load.
        FZMAX (Optional[float]): Maximum allowed wheel load.
    """

    FZMIN: Optional[float] = None
    FZMAX: Optional[float] = None


class LongSlipRange(_ParameterGroup):
    """
    Minimum and maximum valid longitudinal slips.

    Attributes:
        KPUMIN (Optional[float]): Minimum valid wheel slip.
        KPUMAX (Optional[float]): Maximum valid wheel slip.
    """

    KPUMIN: Optional[float] = None
    KPUMAX: Optional[float] = None


class SlipAngleRange(_ParameterGroup):
    """
    Minimum and maximum valid sideslip angles.

    Attributes:
        ALPMIN (Optional[float]): Minimum valid slip angle.
        ALPMAX (Optional[float]): Maximum valid slip angle.
    """

    ALPMIN: Optional[float] = None
    ALPMAX: Optional[float] = None


class InclinationAngleRange(_ParameterGroup):
    """
    Minimum and maximum valid inclination angles.

    Attributes:
        CAMMIN (Optional[float]): Minimum valid camber angle.
        CAMMAX (Optional[float]): Maximum valid camber angle.
    """

    CAMMIN: Optional[float] = None
    CAMMAX: Optional[float] = None


class ScalingCoefficients(_ParameterGroup):
    """
    Magic Formula scaling factors.

    Attributes:
        LFZO (float): Scale factor of nominal (rated) load.
        LCX (float): Scale factor of Fx shape factor.
        LMUX (float): Scale factor of Fx peak friction coefficient.
        LEX (float): Scale factor of Fx curvature factor.
        LKX (float): Scale factor of slip stiffness.
        LHX (float): Scale factor of Fx horizontal shift.
        LVX (float): Scale factor of Fx vertical shift.
        LCY (float): Scale factor of Fy shape factor.
        LMUY (float): Scale factor of Fy peak friction coefficient.
        LEY (float): Scale factor of Fy curvature factor.
        LKY (float): Scale factor of cornering stiffness.
        LKYC (float): Scale factor of camber stiffness.
        LKZC (float): Scale factor of camber moment stiffness.
        LHY (float): Scale factor of Fy horizontal shift.
        LVY (float): Scale factor of Fy vertical shift.
        LTR (float): Scale factor of peak of pneumatic trail.
        LRES (float): Scale factor for offset of residual torque.
        LXAL (float): Scale factor of alpha influence on Fx.
        LYKA (float): Scale factor of kappa influence on Fy.
        LVYKA (float): Scale factor of kappa induced 'ply-steer' Fy.
        LS (float): Scale factor of moment arm of Fx.
        LMX (float): Scale factor of overturning moment.
        LVMX (float): Scale factor of Mx vertical shift.
        LMY (float): Scale factor of rolling resistance torque.
        LMP (Optional[float]): Scale factor of parking moment.
    """

    LFZO: float = 1
    LCX: float = 1
    LMUX: float = 1
    LEX: float = 1
    LKX: float = 1
    LHX: float = 1
    LVX: float = 1
    LCY: float = 1
    LMUY: float = 1
    LEY: float = 1
    LKY: float = 1
    LKYC: float = 1
    LKZC: float = 1
    LHY: float = 1
    LVY: float = 1
    LTR: float = 1
    LRES: float = 1
    LXAL: float = 1
    LYKA: float = 1
    LVYKA: float = 1
    LS: float = 1
    LMX: float = 1
    LVMX: float = 1
    LMY: float = 1
    LMP: Optional[float] = None


class LongitudinalCoefficients(_ParameterGroup):
    """
    Coefficients for evaluating longitudinal force, Fx.

    Attributes:
        PCX1 (float): Shape factor Cf for longitudinal force.
        PDX1 (float): Longitudinal friction Mux at Fznom.
        PDX2 (float): Variation of friction Mux with load.
        PDX3 (float): Variation of friction Mux with camber.
        PEX1 (float): Longitudinal curvature Ef at Fznom.
        PEX2 (float): Variation of curvature Ef with load.
        PEX3 (float): Variation of curvature Ef with load squared.
        PEX4 (float): Factor in curvature Ef while driving.
        PKX1 (float): Longitudinal slip stiffness Kf/Fz at Fznom.
        PKX2 (float): Variation of slip stiffness Kf/Fz with load.
        PKX3 (float): Exponent in slip stiffness Kf/Fz with load.
        PHX1 (float): Horizontal shift Shx at Fznom.
        PHX2 (float): Variation of shift Shx with load.
        PVX1 (float): Vertical shift Sv/Fz at Fznom.
        PVX2 (float): Variation of shift Sv/Fz with load.
        RBX1 (float): Slope factor for combined slip Fx reduction.
        RBX2 (float): Variation of slope Fx reduction with kappa.
        RBX3 (float): Influence of camber on stiffness for Fx combined.
        RCX1 (float): Shape factor for combined slip Fx reduction.
        REX1 (float): Curvature factor of combined Fx.
        REX2 (float): Curvature factor of combined Fx with load.
        RHX1 (float): Shift factor for combined slip Fx reduction.
        PPX1 (float): Linear pressure effect on slip stiffness.
        PPX2 (float): Quadratic pressure effect on slip stiffness.
        PPX3 (float): Linear pressure effect on longitudinal friction.
        PPX4 (float): Quadratic pressure effect on longitudinal friction.
    """

    PCX1: float
    PDX1: float
    PDX2: float
    PDX3: float
    PEX1: float
    PEX2: float
    PEX3: float
    PEX4: float
    PKX1: float
    PKX2: float
    PKX3: float
    PHX1: float
    PHX2: float
    PVX1: float
    PVX2: float
    RBX1: float
    RBX2: float
    RBX3: float
    RCX1: float
    REX1: float
    REX2: float
    RHX1: float
    PPX1: float
    PPX2: float
    PPX3: float
    PPX4: float


class OverturningCoefficients(_ParameterGroup):
    """
    Coefficients for evaluating overturning moment, Mx.

    Attributes:
        QSX1 (float): Overturning moment offset.
        QSX2 (float): Camber induced overturning couple.
        QSX3 (float): Fy induced overturning couple.
        QSX4 (float): Mixed load, lateral force and camber on Mx.
        QSX5 (float): Load effect on Mx with lateral force and camber.
        QSX6 (float): B-factor of load with Mx.
        QSX7 (float): Camber with load on Mx.
        QSX8 (float): Lateral force with load on Mx.
        QSX9 (float): B-factor of lateral force with load on Mx.
        QSX10 (float): Vertical force with camber on Mx.
        QSX11 (float): B-factor of vertical force with camber on Mx.
        QSX12 (Optional[float]): Camber squared induced overturning moment.
        QSX13 (Optional[float]): Lateral force induced overturning moment.
        QSX14 (Optional[float]): Lateral force induced overturning moment with camber.
        PPMX1 (float): Influence of inflation pressure on overturning moment.
    """

    QSX1: float
    QSX2: float
    QSX3: float
    QSX4: float
    QSX5: float
    QSX6: float
    QSX7: float
    QSX8: float
    QSX9: float
    QSX10: float
    QSX11: float
    QSX12: Optional[float] = None
    QSX13: Optional[float] = None
    QSX14: Optional[float] = None
    PPMX1: float


class LateralCoefficients(_ParameterGroup):
    """
    Coefficients for evaluating lateral force, Fy.

    Attributes:
        PCY1 (float): Shape factor Cfy for lateral forces.
        PDY1 (float): Lateral friction Muy.
        PDY2 (float): Variation of friction Muy with load.
        PDY3 (float): Variation of friction Muy with squared camber.
        PEY1 (float): Lateral curvature Efy at Fznom.
        PEY2 (float): Variation of curvature Efy with load.
        PEY3 (float): Zero order camber dependency of curvature Efy.
        PEY4 (float): Variation of curvature Efy with camber.
        PEY5 (float): Camber curvature Efc.
        PKY1 (float): Maximum value of stiffness Kfy/Fznom.
        PKY2 (float): Load at which Kfy reaches maximum value.
        PKY3 (float): Variation of Kfy/Fznom with camber.
        PKY4 (float): Curvature of stiffness Kfy.
        PKY5 (float): Peak stiffness variation with camber squared.
        PKY6 (float): Camber stiffness factor.
        PKY7 (float): Load dependency of camber stiffness factor.
        PHY1 (float): Horizontal shift Shy at Fznom.
        PHY2 (float): Variation of shift Shy with load.
        PVY1 (float): Vertical shift in Svy/Fz at Fznom.
        PVY2 (float): Variation of shift Svy/Fz with load.
        PVY3 (float): Variation of shift Svy/Fz with camber.
        PVY4 (float): Variation of shift Svy/Fz with camber and load.
        RBY1 (float): Slope factor for combined Fy reduction.
        RBY2 (float): Variation of slope Fy reduction with alpha.
        RBY3 (float): Shift term for alpha in slope Fy reduction.
        RBY4 (float): Influence of camber on stiffness of Fy combined.
        RCY1 (float): Shape factor for combined Fy reduction.
        REY1 (float): Curvature factor of combined Fy.
        REY2 (float): Curvature factor of combined Fy with load.
        RHY1 (float): Shift factor for combined Fy reduction.
        RHY2 (float): Shift factor for combined Fy reduction with load.
        RVY1 (float): Kappa induced side force Svyk/Muy*Fz at Fznom.
        RVY2 (float): Variation of Svyk/Muy*Fz with load.
        RVY3 (float): Variation of Svyk/Muy*Fz with camber.
        RVY4 (float): Variation of Svyk/Muy*Fz with alpha.
        RVY5 (float): Variation of Svyk/Muy*Fz with kappa.
        RVY6 (float): Variation of Svyk/Muy*Fz with atan(kappa).
        PPY1 (float): Pressure effect on cornering stiffness magnitude.
        PPY2 (float): Pressure effect on location of cornering stiffness peak.
        PPY3 (float): Linear pressure effect on lateral friction.
        PPY4 (float): Quadratic pressure effect on lateral friction.
        PPY5 (float): Influence of inflation pressure on camber stiffness.
    """

    PCY1: float
    PDY1: float
    PDY2: float
    PDY3: float
    PEY1: float
    PEY2: float
    PEY3: float
    PEY4: float
    PEY5: float
    PKY1: float
    PKY2: float
    PKY3: float
    PKY4: float
    PKY5: float
    PKY6: float
    PKY7: float
    PHY1: float
    PHY2: float
    PVY1: float
    PVY2: float
    PVY3: float
    PVY4: float
    RBY1: float
    RBY2: float
    RBY3: float
    RBY4: float
    RCY1: float
    REY1: float
    REY2: float
    RHY1: float
    RHY2: float
    RVY1: float
    RVY2: float
    RVY3: float
    RVY4: float
    RVY5: float
    RVY6: float
    PPY1: float
    PPY2: float
    PPY3: float
    PPY4: float
    PPY5: float


class RollingCoefficients(_ParameterGroup):
    """
    Coefficients for evaluating rolling resistance moment, My.

    Attributes:
        QSY1 (float): Rolling resistance torque coefficient.
        QSY2 (float): Rolling resistance torque depending on Fx.
        QSY3 (float): Rolling resistance torque depending on speed.
        QSY4 (float): Rolling resistance torque depending on the fourth power of speed.
        QSY5 (float): Rolling resistance torque depending on camber squared.
        QSY6 (float): Rolling resistance torque depending on load and camber squared.
        QSY7 (float): Rolling resistance torque coefficient load dependency.
        QSY8 (float): Rolling resistance torque coefficient pressure dependency.
    """

    QSY1: float
    QSY2: float
    QSY3: float
    QSY4: float
    QSY5: float
    QSY6: float
    QSY7: float
    QSY8: float


class AligningCoefficients(_ParameterGroup):
    """
    Coefficients for evaluating self-aligning moment, Mz.

    Attributes:
        QBZ1 (float): Trail slope factor for trail Bpt at Fznom.
        QBZ2 (float): Variation of slope Bpt with load.
        QBZ3 (float): Variation of slope Bpt with load squared.
        QBZ4 (float): Variation of slope Bpt with camber.
        QBZ5 (float): Variation of slope Bpt with absolute camber.
        QBZ6 (Optional[float]): Variation of slope Bpt with camber squared.
        QBZ9 (float): Slope factor Br of residual torque Mzr.
        QBZ10 (float): Slope factor Br of residual torque Mzr.
        QCZ1 (float): Shape factor Cpt for pneumatic trail.
        QDZ1 (float): Peak trail Dpt = Dpt*(Fz/Fznom*R0).
        QDZ2 (float): Variation of peak Dpt with load.
        QDZ3 (float): Variation of peak Dpt with camber.
        QDZ4 (float): Variation of peak Dpt with camber squared.
        QDZ6 (float): Peak residual torque Dmr = Dmr/(Fz*R0).
        QDZ7 (float): Variation of peak factor Dmr with load.
        QDZ8 (float): Variation of peak factor Dmr with camber.
        QDZ9 (float): Variation of peak factor Dmr with camber and load.
        QDZ10 (float): Variation of peak factor Dmr with camber squared.
        QDZ11 (float): Variation of Dmr with camber squared and load.
        QEZ1 (float): Trail curvature Ept at Fznom.
        QEZ2 (float): Variation of curvature Ept with load.
        QEZ3 (float): Variation of curvature Ept with load squared.
        QEZ4 (float): Variation of curvature Ept with sign of Alpha-t.
        QEZ5 (float): Variation of Ept with camber and sign Alpha-t.
        QHZ1 (float): Trail horizontal shift Sht at Fznom.
        QHZ2 (float): Variation of shift Sht with load.
        QHZ3 (float): Variation of shift Sht with camber.
        QHZ4 (float): Variation of shift Sht with camber and load.
        SSZ1 (float): Nominal value of s/R0:  of Fx on Mz.
        SSZ2 (float): Variation of distance s/R0 with Fy/Fznom.
        SSZ3 (float): Variation of distance s/R0 with camber.
        SSZ4 (float): Variation of distance s/R0 with load and camber.
        PPZ1 (float): Linear pressure effect on pneumatic trail.
        PPZ2 (float): Influence of inflation pressure on residual aligning torque.
    """

    QBZ1: float
    QBZ2: float
    QBZ3: float
    QBZ4: float
    QBZ5: float
    QBZ6: Optional[float] = None
    QBZ9: float
    QBZ10: float
    QCZ1: float
    QDZ1: float
    QDZ2: float
    QDZ3: float
    QDZ4: float
    QDZ6: float
    QDZ7: float
    QDZ8: float
    QDZ9: float
    QDZ10: float
    QDZ11: float
    QEZ1: float
    QEZ2: float
    QEZ3: float
    QEZ4: float
    QEZ5: float
    QHZ1: float
    QHZ2: float
    QHZ3: float
    QHZ4: float
    SSZ1: float
    SSZ2: float
    SSZ3: float
    SSZ4: float
    PPZ1: float
    PPZ2: float


class TurnslipCoefficients(_ParameterGroup):
    """
    Coefficients for turn slip, affecting all forces and moments.

    Attributes:
        PDXP1 (Optional[float]): Peak Fx reduction due to spin parameter.
        PDXP2 (Optional[float]): Peak Fx reduction due to spin with varying load parameter.
        PDXP3 (Optional[float]): Peak Fx reduction due to spin with kappa parameter.
        PKYP1 (Optional[float]): Cornering stiffness reduction due to spin.
        PDYP1 (Optional[float]): Peak Fy reduction due to spin parameter.
        PDYP2 (Optional[float]): Peak Fy reduction due to spin with varying load parameter.
        PDYP3 (Optional[float]): Peak Fy reduction due to spin with alpha parameter.
        PDYP4 (Optional[float]): Peak Fy reduction due to square root of spin parameter.
        PHYP1 (Optional[float]): Fy-alpha curve lateral shift limitation.
        PHYP2 (Optional[float]): Fy-alpha curve maximum lateral shift parameter.
        PHYP3 (Optional[float]): Fy-alpha curve maximum lateral shift varying with load parameter.
        PHYP4 (Optional[float]): Fy-alpha curve maximum lateral shift parameter.
        PECP1 (Optional[float]): Camber w.r.t. spin reduction factor parameter in camber stiffness.
        PECP2 (Optional[float]): Camber w.r.t. spin reduction factor
            varying with load parameter in camber stiffness.
        QDTP1 (Optional[float]): Pneumatic trail reduction factor due to turn slip parameter.
        QCRP1 (Optional[float]): Turning moment at constant turning and zero forward speed parameter.
        QCRP2 (Optional[float]): Turn slip moment (at alpha=90deg) parameter for increase with spin.
        QBRP1 (Optional[float]): Residual (spin) torque reduction factor parameter due to side slip.
        QDRP1 (Optional[float]): Turn slip moment peak magnitude parameter.
    """

    PDXP1: Optional[float] = None
    PDXP2: Optional[float] = None
    PDXP3: Optional[float] = None
    PKYP1: Optional[float] = None
    PDYP1: Optional[float] = None
    PDYP2: Optional[float] = None
    PDYP3: Optional[float] = None
    PDYP4: Optional[float] = None
    PHYP1: Optional[float] = None
    PHYP2: Optional[float] = None
    PHYP3: Optional[float] = None
    PHYP4: Optional[float] = None
    PECP1: Optional[float] = None
    PECP2: Optional[float] = None
    QDTP1: Optional[float] = None
    QCRP1: Optional[float] = None
    QCRP2: Optional[float] = None
    QBRP1: Optional[float] = None
    QDRP1: Optional[float] = None


class TIRParameters(BaseModel):
    """
    Tyre parameters specified in a .TIR file.

    For ease of use, parameters are split into groups.

    Values can be accessed using dot notation:

    Attributes:
        UNITS (Units):
            Units used in the .TIR file.
        MODEL (Model):
            Parameters on the usage of the tyre model.
        DIMENSION (Dimension):
            Tyre dimensions.
        OPERATING_CONDITIONS (OperatingConditions):
            Operating conditions of the tyre.
        INERTIA (Inertia):
            Mass and inertia properties of the tyre and tyre belt.
        VERTICAL (Vertical):
            Vertical stiffness, loaded and effective rolling radius.
        STRUCTURAL (Structural):
            Tyre stiffness, damping, and eigenfrequencies.
        CONTACT_PATCH (ContactPatch):
            Contact length and obstacle enveloping parameters.
        INFLATION_PRESSURE_RANGE (InflationPressureRange):
            Minimum and maximum allowed inflation pressures.
        VERTICAL_FORCE_RANGE (VerticalForceRange):
            Minimum and maximum allowed wheel loads.
        LONG_SLIP_RANGE (LongSlipRange):
            Minimum and maximum valid longitudinal slips.
        SLIP_ANGLE_RANGE (SlipAngleRange):
            Minimum and maximum valid sideslip angles.
        INCLINATION_ANGLE_RANGE (InclinationAngleRange):
            Minimum and maximum valid inclination angles.
        SCALING_COEFFICIENTS (ScalingCoefficients):
            Magic Formula scaling factors.
        LONGITUDINAL_COEFFICIENTS (LongitudinalCoefficients):
            Coefficients for evaluating longitudinal force, Fx.
        OVERTURNING_COEFFICIENTS (OverturningCoefficients):
            Coefficients for evaluating overturning moment, Mx.
        LATERAL_COEFFICIENTS (LateralCoefficients):
            Coefficients for evaluating lateral force, Fy.
        ROLLING_COEFFICIENTS (RollingCoefficients):
            Coefficients for evaluating rolling resistance moment, My.
        ALIGNING_COEFFICIENTS (AligningCoefficients):
            Coefficients for evaluating self-aligning moment, Mz.
        TURNSLIP_COEFFICIENTS (TurnslipCoefficients):
            Coefficients for turn slip, affecting all forces and moments.

    Examples:
        Load tyre parameters from a .TIR file `Example Tyre.tir`,
        and get the inflation pressure of the tyre (`INFLPRES`).

        >>> tir_parameters = TIRParameters.from_file("Example Tyre.tir")
        >>> inflation_pressure = tir_parameters.OPERATING_CONDITIONS.INFLPRES
    """

    UNITS: Units
    MODEL: Model
    DIMENSION: Dimension
    OPERATING_CONDITIONS: OperatingConditions
    INERTIA: Inertia
    VERTICAL: Vertical
    STRUCTURAL: Structural
    CONTACT_PATCH: ContactPatch
    INFLATION_PRESSURE_RANGE: InflationPressureRange
    VERTICAL_FORCE_RANGE: VerticalForceRange
    LONG_SLIP_RANGE: LongSlipRange
    SLIP_ANGLE_RANGE: SlipAngleRange
    INCLINATION_ANGLE_RANGE: InclinationAngleRange
    SCALING_COEFFICIENTS: ScalingCoefficients
    LONGITUDINAL_COEFFICIENTS: LongitudinalCoefficients
    OVERTURNING_COEFFICIENTS: OverturningCoefficients
    LATERAL_COEFFICIENTS: LateralCoefficients
    ROLLING_COEFFICIENTS: RollingCoefficients
    ALIGNING_COEFFICIENTS: AligningCoefficients
    TURNSLIP_COEFFICIENTS: TurnslipCoefficients

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)

    @classmethod
    def from_file(cls, filepath: str) -> Self:
        """
        Generate a TIRParameters object from a .TIR file.

        Uses _TIRReader to parse the .TIR file into a dictionary,
        then converts it to a TIRParameters object.

        Args:
            filepath (str):
                Filepath to the .TIR file.

        Returns:
            self (TIRParameters):
                A TIRParameters object.

        Raises:
            FileNotFoundError:
                If the file is not found.
            ValueError:
                If an error occurs while parsing the .TIR file.
            ValidationError:
                If the data cannot be converted
                into a valid `TIRParameters` object.
        """
        tir_data = _TIRReader().read(filepath)
        return cls.model_validate(tir_data)


class _TIRReader(object):
    """
    Reads and parses .TIR files.
    """

    def read(self, filepath: str) -> dict[str, dict[str, str]]:
        """
        Generate a dictionary from a .TIR file.

        Args:
            filepath (str): Filepath to the .TIR file.

        Returns:
            tir_data (dict[str, dict[str, str]):
                A nested dictionary containing the TIR data.
                The first level of the dictionary is the parameter group name,
                and the second level is the parameter name and value.

        Raises:
            FileNotFoundError:
                If the file is not found.
            ValueError:
                If an error occurs while parsing the .TIR file.
        """
        self.active_parameter_group: Optional[str] = None
        self.data: dict[str, dict[str, str]] = {}

        for line in self._read_lines(filepath):
            self._parse_line(line)

        return self.data

    @staticmethod
    def _read_lines(filepath: str) -> list[str]:
        try:
            with open(filepath, "r") as file:
                return file.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Unable to find file '{filepath}'")

    def _parse_line(self, line: str) -> None:
        """
        Determine the line type and parse it with the appropriate strategy.

        Args:
            line (str): A line from the .TIR file.
        """
        line = line.strip()
        if line.startswith(("$", "!")):
            return
        if line.startswith("["):
            self._parse_parameter_group(line)
        else:
            self._parse_parameter(line)

    def _parse_parameter_group(self, line: str) -> None:
        """
        Parse a parameter group.

        Extract the group name from the line.
        Create a new dictionary for this group.
        Set the current parameter group to this group.

        Args:
            line (str):
                A line from the .TIR file containing a parameter group.

        Raises:
            ValueError:
                If the group name cannot be parsed.
        """
        match = re.search(r"\[([A-Z_]+)\]", line)
        if not match:
            raise ValueError("Invalid parameter group format")
        self.active_parameter_group = str(match.group(1))
        self.data[self.active_parameter_group] = {}

    def _parse_parameter(self, line: str) -> None:
        """
        Parse a parameter.

        Extract the parameter name and value from the line.
        Add the parameter to the current parameter group dictionary.

        Args:
            line (str):
                A line from the .TIR file containg a parameter.

        Raises:
            ValueError:
                If no parameter group is currently active,
                then the line cannot be parsed.
        """
        match = re.search(r"([A-Z0-9_]+)\s*=\s*([^\n\r\$]+)", line)
        if not match:
            return
        parameter, value = match.group(1, 2)
        if not self.active_parameter_group:
            raise ValueError(
                f"Cannot parse parameter {parameter}; no active parameter group"
            )
        self.data[self.active_parameter_group][parameter] = value.strip(" '")

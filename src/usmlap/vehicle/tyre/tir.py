"""
This module provides support for reading tyre data from .TIR files.

The .TIR file format specifies a wide range of tyre parameters
which can be used in the Pacejka Magic Formula.

Documentation for the .TIR file format is available at https://functionbay.com/documentation/onlinehelp/Documents/Tire/MFTyre-MFSwift_Help.pdf, in section 5.3.

The following repositories have been used as a starting point for this module:

- Tire Dynamics (Python):
    https://github.com/JyNing04/Pacejka-tire-model/tree/main

- Magic Formula Tyre Library (MATLAB):
    https://github.com/teasit/magic-formula-tyre-library/tree/main

TODO: Currently, most parameters are marked as `Optional[float]`.
This is due to different requirements
for different versions of the Magic Formula.
Once I better understand these requirements,
many of these parameters will be marked as `float`.
"""

from abc import ABC
from typing import Optional, Self
from pydantic import BaseModel
import re


class _ParameterGroup(ABC, BaseModel):
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
        FITTYP (int):
            Magic Formula version number.
        TYRESIDE (str):
            Position of tyre during measurements.
            "LEFT" or "RIGHT" (default = "LEFT").
        LONGVL (float):
            Reference speed.
        VXLOW (float):
            Lower boundary velocity in slip calculation.
        ROAD_INCREMENT (Optional[float]):
            Increment in road sampling.
        ROAD_DIRECTION (Optional[float]):
            Direction of travelled distance.
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
        UNLOADED_RADIUS (Optional[float]):
            Free tyre radius.
        WIDTH (Optional[float]):
            Nominal section width of the tyre.
        RIM_RADIUS (Optional[float]):
            Nominal rim radius.
        RIM_WIDTH (Optional[float]):
            Rim width.
        ASPECT_RATIO (Optional[float]):
            Nominal aspect ratio.
    """

    UNLOADED_RADIUS: Optional[float] = None
    WIDTH: Optional[float] = None
    RIM_RADIUS: Optional[float] = None
    RIM_WIDTH: Optional[float] = None
    ASPECT_RATIO: Optional[float] = None


class OperatingConditions(_ParameterGroup):
    """
    Operating conditions of the tyre.

    Attributes:
        INFLPRES (Optional[float]):
            Tyre inflation pressure.
        NOMPRES (Optional[float]):
            Nominal pressure used in Magic Formula equations.
    """

    INFLPRES: Optional[float] = None
    NOMPRES: Optional[float] = None


class Inertia(_ParameterGroup):
    """
    Mass and inertia properties of the tyre and tyre belt.

    Attributes:
        MASS (Optional[float]):
            Tyre mass.
        IXX (Optional[float]):
            Tyre diametral moment of inertia.
        IYY (Optional[float]):
            Tyre polar moment of inertia.
        BELT_MASS (Optional[float]):
            Belt mass.
        BELT_IXX (Optional[float]):
            Belt diametral moment of inertia.
        BELT_IYY (Optional[float]):
            Belt polar moment of inertia.
        GRAVITY (Optional[float]):
            Gravity acting on belt in Z direction.
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
        FNOMIN (Optional[float]):
            Nominal wheel load.
        VERTICAL_STIFFNESS (Optional[float]):
            tyre vertical stiffness.
        VERTICAL_DAMPING (Optional[float]):
            tyre vertical damping.
        MC_CONTOUR_A (Optional[float]):
            Motorcycle contour ellipse A.
        MC_CONTOUR_B (Optional[float]):
            Motorcycle contour ellipse B.
        BREFF (Optional[float]):
            Low load stiffness of effective rolling radius.
        DREFF (Optional[float]):
            Peak value of effective rolling radius.
        FREFF (Optional[float]):
            High load stiffness of effective rolling radius.
        Q_RE0 (Optional[float]):
            Ratio of free tyre radius with nominal tyre radius.
        Q_V1 (Optional[float]):
            tyre radius increase with speed.
        Q_V2 (Optional[float]):
            Vertical stiffness increase with speed.
        Q_FZ2 (Optional[float]):
            Quadratic term in load vs. deflection.
        Q_FCX (Optional[float]):
            Longitudinal force influence on vertical stiffness.
        Q_FCY (Optional[float]):
            Lateral force influence on vertical stiffness.
        Q_FCY2 (Optional[float]):
            Explicit load dependency for including
            the lateral force influence on vertical stiffness.
        Q_CAM (Optional[float]):
            Stiffness reduction due to camber.
        Q_CAM1 (Optional[float]):
            Linear load dependent camber angle
            influence on vertical stiffness.
        Q_CAM2 (Optional[float]):
            Quadratic load dependent camber angle
            influence on vertical stiffness.
        Q_CAM3 (Optional[float]):
            Linear load and camber angle dependent
            reduction on vertical stiffness.
        Q_FYS1 (Optional[float]):
            Combined camber angle and side slip angle
            effect on vertical stiffness (constant).
        Q_FYS2 (Optional[float]):
            Combined camber angle and side slip angle
            linear effect on vertical stiffness.
        Q_FYS3 (Optional[float]):
            Combined camber angle and side slip angle
            quadratic effect on vertical stiffness.
        PFZ1 (Optional[float]):
            Pressure effect on vertical stiffness.
        BOTTOM_OFFST (Optional[float]):
            Distance to rim when bottoming starts to occur.
        BOTTOM_STIFF (Optional[float]):
            Vertical stiffness of bottomed tyre.
    """

    FNOMIN: Optional[float] = None
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
        LATERAL_STIFFNESS (Optional[float]):
            Tyre overall lateral stiffness.
        YAW_STIFFNESS (Optional[float]):
            Tyre overall yaw stiffness.
        FREQ_LONG (Optional[float]):
            Undamped frequency fore/aft and vertical mode.
        FREQ_LAT (Optional[float]):
            Undamped frequency lateral mode.
        FREQ_YAW (Optional[float]):
            Undamped frequency yaw and camber mode.
        FREQ_WINDUP (Optional[float]):
            Undamped frequency wind-up mode.
        DAMP_LONG (Optional[float]):
            Dimensionless damping fore/aft and vertical mode.
        DAMP_LAT (Optional[float]):
            Dimensionless damping lateral mode.
        DAMP_YAW (Optional[float]):
            Dimensionless damping yaw and camber mode.
        DAMP_WINDUP (Optional[float]):
            Dimensionless damping wind-up mode.
        DAMP_RESIDUAL (Optional[float]):
            Residual damping (proportional to stiffness).
        DAMP_VLOW (Optional[float]):
            Additional low speed damping (proportional to stiffness).
        Q_BVX (Optional[float]):
            Load and speed influence on in-plane translation stiffness.
        Q_BVT (Optional[float]):
            Load and speed influence on in-plane rotation stiffness.
        PCFX1 (Optional[float]):
            Tyre overall longitudinal stiffness
            vertical deflection dependency linear term.
        PCFX2 (Optional[float]):
            Tyre overall longitudinal stiffness
            vertical deflection dependency quadratic term.
        PCFX3 (Optional[float]):
            Tyre overall longitudinal stiffness pressure dependency.
        PCFY1 (Optional[float]):
            Tyre overall lateral stiffness
            vertical deflection dependency linear term.
        PCFY2 (Optional[float]):
            Tyre overall lateral stiffness
            vertical deflection dependency quadratic term.
        PCFY3 (Optional[float]):
            Tyre overall lateral stiffness pressure dependency.
        PCMZ1 (Optional[float]):
            Tyre overall yaw stiffness pressure dependency.
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
        Q_RA1 (Optional[float]):
            Square root term in contact length equation.
        Q_RA2 (Optional[float]):
            Linear term in contact length equation.
        Q_RB1 (Optional[float]):
            Root term in contact width equation.
        Q_RB2 (Optional[float]):
            Linear term in contact width equation.
        ELLIPS_SHIFT (Optional[float]):
            Scaling of distance between front and rear ellipsoid.
        ELLIPS_LENGTH (Optional[float]):
            Semimajor axis of ellipsoid.
        ELLIPS_HEIGHT (Optional[float]):
            Semiminor axis of ellipsoid.
        ELLIPS_ORDER (Optional[float]):
            Order of ellipsoid.
        ELLIPS_MAX_STEP (Optional[float]):
            Maximum height of road step.
        ELLIPS_NWIDTH (Optional[float]):
            Number of parallel ellipsoids.
        ELLIPS_NLENGTH (Optional[float]):
            Number of ellipsoids at sides of contact patch.
        ENV_C1 (Optional[float]):
            Effective height attenuation.
        ENV_C2 (Optional[float]):
            Effective plane angle attenuation.
        Q_A2 (Optional[float]):
            Linear load term in contact length.
        Q_A1 (Optional[float]):
            Square root load term in contact length.
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
        PRESMIN (Optional[float]):
            Minimum allowed inflation pressure.
        PRESMAX (Optional[float]):
            Maximum allowed inflation pressure.
    """

    PRESMIN: Optional[float] = None
    PRESMAX: Optional[float] = None


class VerticalForceRange(_ParameterGroup):
    """
    Minimum and maximum allowed wheel loads.

    Attributes:
        FZMIN (Optional[float]):
            Minimum allowed wheel load.
        FZMAX (Optional[float]):
            Maximum allowed wheel load.
    """

    FZMIN: Optional[float] = None
    FZMAX: Optional[float] = None


class LongSlipRange(_ParameterGroup):
    """
    Minimum and maximum valid longitudinal slips.

    Attributes:
        KPUMIN (Optional[float]):
            Minimum valid wheel slip.
        KPUMAX (Optional[float]):
            Maximum valid wheel slip.
    """

    KPUMIN: Optional[float] = None
    KPUMAX: Optional[float] = None


class SlipAngleRange(_ParameterGroup):
    """
    Minimum and maximum valid sideslip angles.

    Attributes:
        ALPMIN (Optional[float]):
            Minimum valid slip angle.
        ALPMAX (Optional[float]):
            Maximum valid slip angle.
    """

    ALPMIN: Optional[float] = None
    ALPMAX: Optional[float] = None


class InclinationAngleRange(_ParameterGroup):
    """
    Minimum and maximum valid inclination angles.

    Attributes:
        CAMMIN (Optional[float]):
            Minimum valid camber angle.
        CAMMAX (Optional[float]):
            Maximum valid camber angle.
    """

    CAMMIN: Optional[float] = None
    CAMMAX: Optional[float] = None


class ScalingCoefficients(_ParameterGroup):
    """
    Magic Formula scaling factors.

    Attributes:
        LFZO (Optional[float]):
            Scale factor of nominal (rated) load.
        LCX (Optional[float]):
            Scale factor of Fx shape factor.
        LMUX (Optional[float]):
            Scale factor of Fx peak friction coefficient.
        LEX (Optional[float]):
            Scale factor of Fx curvature factor.
        LKX (Optional[float]):
            Scale factor of slip stiffness.
        LHX (Optional[float]):
            Scale factor of Fx horizontal shift.
        LVX (Optional[float]):
            Scale factor of Fx vertical shift.
        LCY (Optional[float]):
            Scale factor of Fy shape factor.
        LMUY (Optional[float]):
            Scale factor of Fy peak friction coefficient.
        LEY (Optional[float]):
            Scale factor of Fy curvature factor.
        LKY (Optional[float]):
            Scale factor of cornering stiffness.
        LKYC (Optional[float]):
            Scale factor of camber stiffness.
        LKZC (Optional[float]):
            Scale factor of camber moment stiffness.
        LHY (Optional[float]):
            Scale factor of Fy horizontal shift.
        LVY (Optional[float]):
            Scale factor of Fy vertical shift.
        LTR (Optional[float]):
            Scale factor of Peak of pneumatic trail.
        LRES (Optional[float]):
            Scale factor for offset of residual torque.
        LXAL (Optional[float]):
            Scale factor of alpha influence on Fx.
        LYKA (Optional[float]):
            Scale factor of alpha influence on Fx.
        LVYKA (Optional[float]):
            Scale factor of kappa induced Fy.
        LS (Optional[float]):
            Scale factor of Moment arm of Fx.
        LMX (Optional[float]):
            Scale factor of overturning moment.
        LVMX (Optional[float]):
            Scale factor of Mx vertical shift.
        LMY (Optional[float]):
            Scale factor of rolling resistance torque.
        LMP (Optional[float]):
            Scale factor of parking moment.
    """

    LFZO: Optional[float] = None
    LCX: Optional[float] = None
    LMUX: Optional[float] = None
    LEX: Optional[float] = None
    LKX: Optional[float] = None
    LHX: Optional[float] = None
    LVX: Optional[float] = None
    LCY: Optional[float] = None
    LMUY: Optional[float] = None
    LEY: Optional[float] = None
    LKY: Optional[float] = None
    LKYC: Optional[float] = None
    LKZC: Optional[float] = None
    LHY: Optional[float] = None
    LVY: Optional[float] = None
    LTR: Optional[float] = None
    LRES: Optional[float] = None
    LXAL: Optional[float] = None
    LYKA: Optional[float] = None
    LVYKA: Optional[float] = None
    LS: Optional[float] = None
    LMX: Optional[float] = None
    LVMX: Optional[float] = None
    LMY: Optional[float] = None
    LMP: Optional[float] = None


class LongitudinalCoefficients(_ParameterGroup):
    """
    Coefficients for evaluating longitudinal force, Fx.

    Attributes:
        PCX1 (Optional[float]):
            Shape factor Cf for longitudinal force.
        PDX1 (Optional[float]):
            Longitudinal friction Mux at Fznom.
        PDX2 (Optional[float]):
            Variation of friction Mux with load.
        PDX3 (Optional[float]):
            Variation of friction Mux with camber.
        PEX1 (Optional[float]):
            Longitudinal curvature Ef at Fznom.
        PEX2 (Optional[float]):
            Variation of curvature Ef with load.
        PEX3 (Optional[float]):
            Variation of curvature Ef with load squared.
        PEX4 (Optional[float]):
            Factor in curvature Ef while driving.
        PKX1 (Optional[float]):
            Longitudinal slip stiffness Kf/Fz at Fznom.
        PKX2 (Optional[float]):
            Variation of slip stiffness Kf/Fz with load.
        PKX3 (Optional[float]):
            Exponent in slip stiffness Kf/Fz with load.
        PHX1 (Optional[float]):
            Horizontal shift Shx at Fznom.
        PHX2 (Optional[float]):
            Variation of shift Shx with load.
        PVX1 (Optional[float]):
            Vertical shift Sv/Fz at Fznom.
        PVX2 (Optional[float]):
            Variation of shift Sv/Fz with load.
        RBX1 (Optional[float]):
            Slope factor for combined slip Fx reduction.
        RBX2 (Optional[float]):
            Variation of slope Fx reduction with kappa.
        RBX3 (Optional[float]):
            Influence of camber on stiffness for Fx combined.
        RCX1 (Optional[float]):
            Shape factor for combined slip Fx reduction.
        REX1 (Optional[float]):
            Curvature factor of combined Fx.
        REX2 (Optional[float]):
            Curvature factor of combined Fx with load.
        RHX1 (Optional[float]):
            Shift factor for combined slip Fx reduction.
        PPX1 (Optional[float]):
            Linear pressure effect on slip stiffness.
        PPX2 (Optional[float]):
            Quadratic pressure effect on slip stiffness.
        PPX3 (Optional[float]):
            Linear pressure effect on longitudinal friction.
        PPX4 (Optional[float]):
            Quadratic pressure effect on longitudinal friction.
    """

    PCX1: Optional[float] = None
    PDX1: Optional[float] = None
    PDX2: Optional[float] = None
    PDX3: Optional[float] = None
    PEX1: Optional[float] = None
    PEX2: Optional[float] = None
    PEX3: Optional[float] = None
    PEX4: Optional[float] = None
    PKX1: Optional[float] = None
    PKX2: Optional[float] = None
    PKX3: Optional[float] = None
    PHX1: Optional[float] = None
    PHX2: Optional[float] = None
    PVX1: Optional[float] = None
    PVX2: Optional[float] = None
    RBX1: Optional[float] = None
    RBX2: Optional[float] = None
    RBX3: Optional[float] = None
    RCX1: Optional[float] = None
    REX1: Optional[float] = None
    REX2: Optional[float] = None
    RHX1: Optional[float] = None
    PPX1: Optional[float] = None
    PPX2: Optional[float] = None
    PPX3: Optional[float] = None
    PPX4: Optional[float] = None


class OverturningCoefficients(_ParameterGroup):
    """
    Coefficients for evaluating overturning moment, Mx.

    Attributes:
        QSX1 (Optional[float]):
            Overturning moment offset.
        QSX2 (Optional[float]):
            Camber induced overturning couple.
        QSX3 (Optional[float]):
            Fy induced overturning couple.
        QSX4 (Optional[float]):
            Mixed load, lateral force and camber on Mx.
        QSX5 (Optional[float]):
            Load effect on Mx with lateral force and camber.
        QSX6 (Optional[float]):
            B-factor of load with Mx.
        QSX7 (Optional[float]):
            Camber with load on Mx.
        QSX8 (Optional[float]):
            Lateral force with load on Mx.
        QSX9 (Optional[float]):
            B-factor of lateral force with load on Mx.
        QSX10 (Optional[float]):
            Vertical force with camber on Mx.
        QSX11 (Optional[float]):
            B-factor of vertical force with camber on Mx.
        QSX12 (Optional[float]):
            Camber squared induced overturning moment.
        QSX13 (Optional[float]):
            Lateral force induced overturning moment.
        QSX14 (Optional[float]):
            Lateral force induced overturning moment with camber.
        PPMX1 (Optional[float]):
            Influence of inflation pressure on overturning moment.
    """

    QSX1: Optional[float] = None
    QSX2: Optional[float] = None
    QSX3: Optional[float] = None
    QSX4: Optional[float] = None
    QSX5: Optional[float] = None
    QSX6: Optional[float] = None
    QSX7: Optional[float] = None
    QSX8: Optional[float] = None
    QSX9: Optional[float] = None
    QSX10: Optional[float] = None
    QSX11: Optional[float] = None
    QSX12: Optional[float] = None
    QSX13: Optional[float] = None
    QSX14: Optional[float] = None
    PPMX1: Optional[float] = None


class LateralCoefficients(_ParameterGroup):
    """
    Coefficients for evaluating lateral force, Fy.

    Attributes:
        PCY1 (Optional[float]):
            Shape factor Cfy for lateral forces.
        PDY1 (Optional[float]):
            Lateral friction Muy.
        PDY2 (Optional[float]):
            Variation of friction Muy with load.
        PDY3 (Optional[float]):
            Variation of friction Muy with squared camber.
        PEY1 (Optional[float]):
            Lateral curvature Efy at Fznom.
        PEY2 (Optional[float]):
            Variation of curvature Efy with load.
        PEY3 (Optional[float]):
            Zero order camber dependency of curvature Efy.
        PEY4 (Optional[float]):
            Variation of curvature Efy with camber.
        PEY5 (Optional[float]):
            Camber curvature Efc.
        PKY1 (Optional[float]):
            Maximum value of stiffness Kfy/Fznom.
        PKY2 (Optional[float]):
            Load at which Kfyreaches maximum value.
        PKY3 (Optional[float]):
            Variation of Kfy/Fznom with camber.
        PKY4 (Optional[float]):
            Curvature of stiffness Kfy.
        PKY5 (Optional[float]):
            Peak stiffness variation with camber squared.
        PKY6 (Optional[float]):
            Camber stiffness factor.
        PKY7 (Optional[float]):
            Load dependency of camber stiffness factor.
        PHY1 (Optional[float]):
            Horizontal shift Shy at Fznom.
        PHY2 (Optional[float]):
            Variation of shift Shy with load.
        PVY1 (Optional[float]):
            Vertical shift in Svy/Fz at Fznom.
        PVY2 (Optional[float]):
            Variation of shift Svy/Fz with load.
        PVY3 (Optional[float]):
            Variation of shift Svy/Fz with camber.
        PVY4 (Optional[float]):
            Variation of shift Svy/Fz with camber and load.
        RBY1 (Optional[float]):
            Slope factor for combined Fy reduction.
        RBY2 (Optional[float]):
            Variation of slope Fy reduction with alpha.
        RBY3 (Optional[float]):
            Shift term for alpha in slope Fy reduction.
        RBY4 (Optional[float]):
            Influence of camber on stiffness of Fy combined.
        RCY1 (Optional[float]):
            Shape factor for combined Fy reduction.
        REY1 (Optional[float]):
            Curvature factor of combined Fy.
        REY2 (Optional[float]):
            Curvature factor of combined Fy with load.
        RHY1 (Optional[float]):
            Shift factor for combined Fy reduction.
        RHY2 (Optional[float]):
            Shift factor for combined Fy reduction with load.
        RVY1 (Optional[float]):
            Kappa induced side force Svyk/Muy*Fz at Fznom.
        RVY2 (Optional[float]):
            Variation of Svyk/Muy*Fz with load.
        RVY3 (Optional[float]):
            Variation of Svyk/Muy*Fz with camber.
        RVY4 (Optional[float]):
            Variation of Svyk/Muy*Fz with alpha.
        RVY5 (Optional[float]):
            Variation of Svyk/Muy*Fz with kappa.
        RVY6 (Optional[float]):
            Variation of Svyk/Muy*Fz with atan(kappa).
        PPY1 (Optional[float]):
            Pressure effect on cornering stiffness magnitude.
        PPY2 (Optional[float]):
            Pressure effect on location of cornering stiffness peak.
        PPY3 (Optional[float]):
            Linear pressure effect on lateral friction.
        PPY4 (Optional[float]):
            Quadratic pressure effect on lateral friction.
        PPY5 (Optional[float]):
            Influence of inflation pressure on camber stiffness.
    """

    PCY1: Optional[float] = None
    PDY1: Optional[float] = None
    PDY2: Optional[float] = None
    PDY3: Optional[float] = None
    PEY1: Optional[float] = None
    PEY2: Optional[float] = None
    PEY3: Optional[float] = None
    PEY4: Optional[float] = None
    PEY5: Optional[float] = None
    PKY1: Optional[float] = None
    PKY2: Optional[float] = None
    PKY3: Optional[float] = None
    PKY4: Optional[float] = None
    PKY5: Optional[float] = None
    PKY6: Optional[float] = None
    PKY7: Optional[float] = None
    PHY1: Optional[float] = None
    PHY2: Optional[float] = None
    PVY1: Optional[float] = None
    PVY2: Optional[float] = None
    PVY3: Optional[float] = None
    PVY4: Optional[float] = None
    RBY1: Optional[float] = None
    RBY2: Optional[float] = None
    RBY3: Optional[float] = None
    RBY4: Optional[float] = None
    RCY1: Optional[float] = None
    REY1: Optional[float] = None
    REY2: Optional[float] = None
    RHY1: Optional[float] = None
    RHY2: Optional[float] = None
    RVY1: Optional[float] = None
    RVY2: Optional[float] = None
    RVY3: Optional[float] = None
    RVY4: Optional[float] = None
    RVY5: Optional[float] = None
    RVY6: Optional[float] = None
    PPY1: Optional[float] = None
    PPY2: Optional[float] = None
    PPY3: Optional[float] = None
    PPY4: Optional[float] = None
    PPY5: Optional[float] = None


class RollingCoefficients(_ParameterGroup):
    """
    Coefficients for evaluating rolling resistance moment, My.

    Attributes:
        QSY1 (Optional[float]):
            Rolling resistance torque coefficient.
        QSY2 (Optional[float]):
            Rolling resistance torque depending on Fx.
        QSY3 (Optional[float]):
            Rolling resistance torque depending on speed.
        QSY4 (Optional[float]):
            Rolling resistance torque depending on speed ^ 4.
        QSY5 (Optional[float]):
            Rolling resistance torque depending on camber squared.
        QSY6 (Optional[float]):
            Rolling resistance torque depending on load and camber squared.
        QSY7 (Optional[float]):
            Rolling resistance torque coefficient load dependency.
        QSY8 (Optional[float]):
            Rolling resistance torque coefficient pressure dependency.
    """

    QSY1: Optional[float] = None
    QSY2: Optional[float] = None
    QSY3: Optional[float] = None
    QSY4: Optional[float] = None
    QSY5: Optional[float] = None
    QSY6: Optional[float] = None
    QSY7: Optional[float] = None
    QSY8: Optional[float] = None


class AligningCoefficients(_ParameterGroup):
    """
    Coefficients for evaluating self-aligning moment, Mz.

    Attributes:
        QBZ1 (Optional[float]):
            Trail slope factor for trail Bpt at Fznom.
        QBZ2 (Optional[float]):
            Variation of slope Bpt with load.
        QBZ3 (Optional[float]):
            Variation of slope Bpt with load squared.
        QBZ4 (Optional[float]):
            Variation of slope Bpt with camber.
        QBZ5 (Optional[float]):
            Variation of slope Bpt with absolute camber.
        QBZ9 (Optional[float]):
            Slope factor Br of residual torque Mzr.
        QBZ10 (Optional[float]):
            Slope factor Br of residual torque Mzr.
        QCZ1 (Optional[float]):
            Shape factor Cpt for pneumatic trail.
        QDZ1 (Optional[float]):
            Peak trail Dpt = Dpt*(Fz/Fznom*R0).
        QDZ2 (Optional[float]):
            Variation of peak Dpt with load.
        QDZ3 (Optional[float]):
            Variation of peak Dpt with camber.
        QDZ4 (Optional[float]):
            Variation of peak Dpt with camber squared.
        QDZ6 (Optional[float]):
            Peak residual torque Dmr = Dmr/(Fz*R0).
        QDZ7 (Optional[float]):
            Variation of peak factor Dmr with load.
        QDZ8 (Optional[float]):
            Variation of peak factor Dmr with camber.
        QDZ9 (Optional[float]):
            Variation of peak factor Dmr with camber and load.
        QDZ10 (Optional[float]):
            Variation of peak factor Dmr with camber squared.
        QDZ11 (Optional[float]):
            Variation of Dmr with camber squared and load.
        QEZ1 (Optional[float]):
            Trail curvature Ept at Fznom.
        QEZ2 (Optional[float]):
            Variation of curvature Ept with load.
        QEZ3 (Optional[float]):
            Variation of curvature Ept with load squared.
        QEZ4 (Optional[float]):
            Variation of curvature Ept with sign of Alpha-t.
        QEZ5 (Optional[float]):
            Variation of Ept with camber and sign Alpha-t.
        QHZ1 (Optional[float]):
            Trail horizontal shift Sht at Fznom.
        QHZ2 (Optional[float]):
            Variation of shift Sht with load.
        QHZ3 (Optional[float]):
            Variation of shift Sht with camber.
        QHZ4 (Optional[float]):
            Variation of shift Sht with camber and load.
        SSZ1 (Optional[float]):
            Nominal value of s/R0: effect of Fx on Mz.
        SSZ2 (Optional[float]):
            Variation of distance s/R0 with Fy/Fznom.
        SSZ3 (Optional[float]):
            Variation of distance s/R0 with camber.
        SSZ4 (Optional[float]):
            Variation of distance s/R0 with load and camber.
        PPZ1 (Optional[float]):
            Linear pressure effect on pneumatic trail.
        PPZ2 (Optional[float]):
            Influence of inflation pressure on residual aligning torque.
    """

    QBZ1: Optional[float] = None
    QBZ2: Optional[float] = None
    QBZ3: Optional[float] = None
    QBZ4: Optional[float] = None
    QBZ5: Optional[float] = None
    QBZ9: Optional[float] = None
    QBZ10: Optional[float] = None
    QCZ1: Optional[float] = None
    QDZ1: Optional[float] = None
    QDZ2: Optional[float] = None
    QDZ3: Optional[float] = None
    QDZ4: Optional[float] = None
    QDZ6: Optional[float] = None
    QDZ7: Optional[float] = None
    QDZ8: Optional[float] = None
    QDZ9: Optional[float] = None
    QDZ10: Optional[float] = None
    QDZ11: Optional[float] = None
    QEZ1: Optional[float] = None
    QEZ2: Optional[float] = None
    QEZ3: Optional[float] = None
    QEZ4: Optional[float] = None
    QEZ5: Optional[float] = None
    QHZ1: Optional[float] = None
    QHZ2: Optional[float] = None
    QHZ3: Optional[float] = None
    QHZ4: Optional[float] = None
    SSZ1: Optional[float] = None
    SSZ2: Optional[float] = None
    SSZ3: Optional[float] = None
    SSZ4: Optional[float] = None
    PPZ1: Optional[float] = None
    PPZ2: Optional[float] = None


class TurnslipCoefficients(_ParameterGroup):
    """
    Coefficients for turn slip, affecting all forces and moments.

    Attributes:
        PDXP1 (Optional[float]):
            Peak Fx reduction due to spin parameter.
        PDXP2 (Optional[float]):
            Peak Fx reduction due to spin with varying load parameter.
        PDXP3 (Optional[float]):
            Peak Fx reduction due to spin with kappa parameter.
        PKYP1 (Optional[float]):
            Cornering stiffness reduction due to spin.
        PDYP1 (Optional[float]):
            Peak Fy reduction due to spin parameter.
        PDYP2 (Optional[float]):
            Peak Fy reduction due to spin with varying load parameter.
        PDYP3 (Optional[float]):
            Peak Fy reduction due to spin with alpha parameter.
        PDYP4 (Optional[float]):
            Peak Fy reduction due to square root of spin parameter.
        PHYP1 (Optional[float]):
            Fy-alpha curve lateral shift limitation.
        PHYP2 (Optional[float]):
            Fy-alpha curve maximum lateral shift parameter.
        PHYP3 (Optional[float]):
            Fy-alpha curve maximum lateral shift varying with load parameter.
        PHYP4 (Optional[float]):
            Fy-alpha curve maximum lateral shift parameter.
        PECP1 (Optional[float]):
            Camber w.r.t. spin reduction factor parameter in camber stiffness.
        PECP2 (Optional[float]):
            Camber w.r.t. spin reduction factor
            varying with load parameter in camber stiffness.
        QDTP1 (Optional[float]):
            Pneumatic trail reduction factor due to turn slip parameter.
        QCRP1 (Optional[float]):
            Turning moment at constant turning and zero forward speed parameter.
        QCRP2 (Optional[float]):
            Turn slip moment (at alpha=90deg) parameter for increase with spin.
        QBRP1 (Optional[float]):
            Residual (spin) torque reduction factor parameter due to side slip.
        QDRP1 (Optional[float]):
            Turn slip moment peak magnitude parameter.
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


class _TIRReader:
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

    def _read_lines(self, filepath: str) -> list[str]:
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

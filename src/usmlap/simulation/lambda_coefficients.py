"""
This module defines lambda coefficients for a simulation.

These are used to directly modify results in order to investigate sensitivities.
"""

from dataclasses import dataclass


@dataclass
class LambdaCoefficients(object):
    """
    Lambda coefficients for a simulation.

    Attributes:
        longitudinal_grip (float): Longitudinal grip coefficient.
        lateral_grip (float): Lateral grip coefficient.
        motor_torque (float): Motor torque coefficient (does not affect energy consumption).
    """

    longitudinal_grip: float = 1
    lateral_grip: float = 1
    motor_torque: float = 1

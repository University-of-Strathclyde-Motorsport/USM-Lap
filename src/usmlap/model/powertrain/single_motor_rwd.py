"""
This module defines a single-motor, rear-wheel drive powertrain.
"""

from ..context import Context
from .interface import PowertrainModelInterface


class SingleMotorRWD(PowertrainModelInterface):
    """
    Powertrain model for a single-motor vehicle.
    """

    def drive_force(self, ctx: Context, velocity: float) -> float:
        motor_speed = ctx.vehicle.velocity_to_motor_speed(velocity)
        motor_torque = ctx.vehicle.powertrain.get_motor_torque(
            state_of_charge=ctx.state.state_of_charge, motor_speed=motor_speed
        )
        drive_force = ctx.vehicle.motor_torque_to_drive_force(motor_torque)

        return drive_force

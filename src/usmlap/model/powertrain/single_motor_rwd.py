"""
This module defines a single-motor, rear-wheel drive powertrain.
"""

from ..context import NodeContext
from .interface import PowertrainModelInterface


class SingleMotorRWD(PowertrainModelInterface):
    """
    Powertrain model for a single-motor vehicle.
    """

    def required_torque(self, ctx: NodeContext, drive_force: float) -> float:
        return ctx.vehicle.traction_force_to_motor_torque(drive_force)

    def required_current(self, ctx: NodeContext, torque: float) -> float:
        return ctx.vehicle.powertrain.motor.get_current(torque)

    def motor_torque(self, ctx: NodeContext, velocity: float) -> float:
        motor_speed = ctx.vehicle.velocity_to_motor_speed(velocity)
        torque = ctx.vehicle.powertrain.get_motor_torque(
            ctx.state.cell_state, motor_speed
        )
        return torque

    def drive_force(self, ctx: NodeContext, velocity: float) -> float:
        motor_speed = ctx.vehicle.velocity_to_motor_speed(velocity)
        motor_torque = ctx.vehicle.powertrain.get_motor_torque(
            ctx.state.cell_state, motor_speed
        )
        drive_force = ctx.vehicle.motor_torque_to_drive_force(motor_torque)

        return drive_force

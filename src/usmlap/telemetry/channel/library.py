"""
This module defines primitive telemetry channels which extract values from a telemetry solution.
"""

from pint import UnitRegistry

import usmlap.telemetry.channel.functions as fcn
from usmlap.solver import SolutionNode
from usmlap.telemetry import TelemetrySolution

from .channel import DerivedDataChannel, PrimitiveDataChannel

ureg = UnitRegistry()


class Velocity(
    PrimitiveDataChannel, unit=ureg.meter / ureg.second, label="Velocity"
):
    """Velocity of the vehicle."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.average_velocity


class MaximumVelocity(
    PrimitiveDataChannel,
    unit=ureg.meter / ureg.second,
    label="Maximum Velocity",
):
    """Maximum velocity of the vehicle."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.maximum_velocity


class Position(PrimitiveDataChannel, unit=ureg.meter, label="Position"):
    """Position of the vehicle."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.track_node.position


class NodeTime(PrimitiveDataChannel, unit=ureg.millisecond, label="Node Time"):
    """Time taken to traverse the node."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.time


class Time(DerivedDataChannel, unit=ureg.second, label="Time"):
    """Cumulative time."""

    @classmethod
    def channel_fcn(cls, solution: TelemetrySolution) -> list[float]:
        return fcn.cumulative_sum(NodeTime())(solution)


class Curvature(PrimitiveDataChannel, unit=1 / ureg.meter, label="Curvature"):
    """Curvature of the track."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.track_node.curvature


class LateralAcceleration(
    PrimitiveDataChannel,
    unit=ureg.meter / ureg.second**2,
    label="Lateral Acceleration",
):
    """Lateral acceleration of the vehicle."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.lateral_acceleration


class LongitudinalAcceleration(
    PrimitiveDataChannel,
    unit=ureg.meter / ureg.second**2,
    label="Longitudinal Acceleration",
):
    """Longitudinal acceleration of the vehicle."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.longitudinal_acceleration


class Drag(PrimitiveDataChannel, unit=ureg.newton, label="Drag"):
    """Aerodynamic drag force."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.calculated_vehicle_state.drag


class AccumulatorCurrent(
    PrimitiveDataChannel, unit=ureg.ampere, label="Accumulator Current"
):
    """Current drawn from the accumulator."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.calculated_vehicle_state.accumulator_current


class MotorTorque(
    PrimitiveDataChannel, unit=ureg.newton * ureg.meter, label="Motor Torque"
):
    """Torque output of the motor."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.calculated_vehicle_state.motor_torque


class MotorPower(PrimitiveDataChannel, unit=ureg.kilowatt, label="Motor Power"):
    """Power output of the motor."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.calculated_vehicle_state.motor_power

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
        return node.get_calculated_vehicle_state().drag


class StateOfCharge(
    PrimitiveDataChannel, unit=ureg.dimensionless, label="State of Charge"
):
    """State of charge of the battery."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.transient_variables.cell_state.soc


class CellTemperature(
    PrimitiveDataChannel, unit=ureg.degree_celsius, label="Cell Temperature"
):
    """Temperature of the battery cells."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.transient_variables.cell_state.temperature


class AccumulatorCurrent(
    PrimitiveDataChannel, unit=ureg.ampere, label="Accumulator Current"
):
    """Current drawn from the accumulator."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.get_calculated_vehicle_state().accumulator_current


class MotorTorque(
    PrimitiveDataChannel, unit=ureg.newton * ureg.meter, label="Motor Torque"
):
    """Torque output of the motor."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.get_calculated_vehicle_state().motor_torque


class MotorPower(PrimitiveDataChannel, unit=ureg.kilowatt, label="Motor Power"):
    """Power output of the motor."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.get_calculated_vehicle_state().motor_power


class CoolingPower(
    PrimitiveDataChannel, unit=ureg.kilowatt, label="Cooling Power"
):
    """Power output of the cooling system."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.get_calculated_vehicle_state().cooling_power


class HeatingPower(
    PrimitiveDataChannel, unit=ureg.kilowatt, label="Heating Power"
):
    """Heating power of the cells."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.get_calculated_vehicle_state().heating_power


class NetHeatingPower(
    PrimitiveDataChannel, unit=ureg.kilowatt, label="Net Heating Power"
):
    """Net heating power of the cells."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.get_calculated_vehicle_state().net_heating_power


class LongLT(
    PrimitiveDataChannel,
    unit=ureg.meter / ureg.second**2,
    label="Longitudinal LT",
):
    """Longitudinal load transfer of the vehicle."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.get_calculated_vehicle_state().long_lt


class LatLT(
    PrimitiveDataChannel, unit=ureg.meter / ureg.second**2, label="Lateral LT"
):
    """Lateral load transfer of the vehicle."""

    @classmethod
    def read_value(cls, node: SolutionNode) -> float:
        return node.get_calculated_vehicle_state().lat_lt

"""
This module defines a common interface for vehicle models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from usmlap.utils.datatypes import FourCorner
from usmlap.vehicle.aero import AeroAttitude

from ..context import NodeContext
from ..powertrain import PowertrainModelInterface, SingleMotorRWD
from ..vehicle_state import FullVehicleState


@dataclass
class VehicleModelInterface(ABC):
    """
    Abstract base class for vehicle models.
    """

    powertrain: PowertrainModelInterface = SingleMotorRWD()

    @staticmethod
    def weight(ctx: NodeContext) -> float:
        return ctx.vehicle.total_mass * ctx.environment.gravity

    @staticmethod
    def centripetal_force(ctx: NodeContext, velocity: float) -> float:
        return ctx.vehicle.total_mass * ctx.node.curvature * velocity**2

    @staticmethod
    def aero_attitude(ctx: NodeContext, velocity: float) -> AeroAttitude:
        return AeroAttitude(
            velocity=velocity, air_density=ctx.environment.air_density
        )

    def required_fy(self, ctx: NodeContext, velocity: float) -> float:
        weight = self.weight(ctx)
        centripetal_force = self.centripetal_force(ctx, velocity)
        return ctx.node.y_to_y(centripetal_force) - ctx.node.z_to_y(weight)

    def resistive_forces(
        self, ctx: NodeContext, velocity: float
    ) -> tuple[float, float]:
        """
        Get the total resistive forces acting on the vehicle.
        Returns a tuple of body and aerodynamic forces.

        Args:
            ctx (NodeContext): The simulation context.
            velocity (float): The vehicle's velocity.

        Returns:
            body_force (float):
                The resistive force acting through the centre of mass.
            aero_force (float):
                The resistive force acting through the centre of pressure.
        """
        weight = self.weight(ctx)
        body_force = ctx.node.z_to_x(weight)

        aero_attitude = self.aero_attitude(ctx, velocity)
        aero_force = ctx.vehicle.aero.get_drag(aero_attitude)

        return body_force, aero_force

    def normal_forces(
        self, ctx: NodeContext, velocity: float
    ) -> tuple[float, float]:
        """
        Get the total normal forces acting on the tyres.
        Returns a tuple of body and aerodynamic forces.

        Args:
            ctx (NodeContext): The simulation context.
            velocity (float): The vehicle's velocity.

        Returns:
            body_force (float):
                The normal force acting through the centre of mass.
            aero_force (float):
                The normal force acting through the centre of pressure.
        """

        weight = self.weight(ctx)
        centripetal_force = self.centripetal_force(ctx, velocity)
        body_force = ctx.node.z_to_z(weight) + ctx.node.y_to_z(
            centripetal_force
        )

        aero_attitude = self.aero_attitude(ctx, velocity)
        aero_force = ctx.vehicle.aero.get_downforce(aero_attitude)

        return body_force, aero_force

    @abstractmethod
    def normal_loads(
        self, ctx: NodeContext, velocity: float, ax: float, ay: float
    ) -> FourCorner[float]: ...

    @abstractmethod
    def lateral_traction(
        self, ctx: NodeContext, velocity: float, ax: float, ay: float
    ) -> float: ...

    @abstractmethod
    def longitudinal_traction(
        self, ctx: NodeContext, velocity: float, ax: float, ay: float
    ) -> float: ...

    @abstractmethod
    def braking_traction(
        self, ctx: NodeContext, velocity: float, ax: float, ay: float
    ) -> float: ...

    def evaluate_full_vehicle_state(
        self, ctx: NodeContext, velocity: float, ax: float, ay: float
    ) -> FullVehicleState:
        weight = self.weight(ctx)
        centripetal_force = self.centripetal_force(ctx, velocity)
        body_fz, aero_fz = self.normal_forces(ctx, velocity)
        body_fx, aero_fx = self.resistive_forces(ctx, velocity)
        drive_force = max(
            body_fx + aero_fx + ax * ctx.vehicle.equivalent_mass, 0
        )
        normal_loads = self.normal_loads(ctx, velocity, ax, ay)
        motor_speed = ctx.vehicle.velocity_to_motor_speed(velocity)
        motor_torque = self.powertrain.required_torque(ctx, drive_force)
        motor_power = motor_speed * motor_torque
        accu_power = (
            motor_power / ctx.vehicle.powertrain.get_powertrain_efficiency()
        )
        accu_current = (
            accu_power
            / ctx.vehicle.powertrain.accumulator.get_voltage(
                ctx.state.cell_state.soc
            )
        )
        heating_power = ctx.vehicle.powertrain.accumulator.heating_power(
            ctx.state.cell_state, accu_current
        )
        cooling_power = ctx.vehicle.powertrain.cooling_rate(
            ctx.state.cell_temperature, ctx.environment.ambient_temperature
        )

        return FullVehicleState(
            velocity=velocity,
            ax=ax,
            ay=ay,
            weight=weight,
            centripetal_force=centripetal_force,
            downforce=aero_fz,
            drag=aero_fx,
            resistive_fx=(body_fx + aero_fx),
            required_fy=self.required_fy(ctx, velocity),
            normal_force=body_fz,
            normal_loads=normal_loads,
            motor_speed=motor_speed,
            motor_torque=motor_torque,
            motor_power=motor_power,
            accumulator_current=accu_current,
            heating_power=heating_power,
            cooling_power=cooling_power,
        )

"""
This module defines the interface for vehicle models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from usmlap.simulation.vehicle_state import FullVehicleState
from usmlap.vehicle.aero import AeroAttitude

from .context import Context
from .powertrain import PowertrainModelInterface, SingleMotorPowertrain


@dataclass
class VehicleModelInterface(ABC):
    """
    Abstract base class for vehicle models.
    """

    powertrain: PowertrainModelInterface = SingleMotorPowertrain()

    @staticmethod
    def weight(ctx: Context) -> float:
        return ctx.vehicle.total_mass * ctx.environment.gravity

    @staticmethod
    def centripetal_force(ctx: Context, velocity: float) -> float:
        return ctx.vehicle.total_mass * ctx.node.curvature * velocity**2

    @staticmethod
    def aero_attitude(ctx: Context, velocity: float) -> AeroAttitude:
        return AeroAttitude(
            velocity=velocity, air_density=ctx.environment.air_density
        )

    def required_fy(self, ctx: Context, velocity: float) -> float:
        weight = self.weight(ctx)
        centripetal_force = self.centripetal_force(ctx, velocity)
        return ctx.node.y_to_y(centripetal_force) - ctx.node.z_to_y(weight)

    def resistive_forces(
        self, ctx: Context, velocity: float
    ) -> tuple[float, float]:
        """
        Get the total resistive forces acting on the vehicle.
        Returns a tuple of body and aerodynamic forces.

        Args:
            ctx (Context): The simulation context.
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
        self, ctx: Context, velocity: float
    ) -> tuple[float, float]:
        """
        Get the total normal forces acting on the tyres.
        Returns a tuple of body and aerodynamic forces.

        Args:
            ctx (Context): The simulation context.
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
    def lateral_traction_limit(
        self, ctx: Context, velocity: float
    ) -> float: ...

    @abstractmethod
    def traction_limited_acceleration(
        self, ctx: Context, velocity: float
    ) -> float: ...

    @abstractmethod
    def traction_limited_braking(
        self, ctx: Context, velocity: float
    ) -> float: ...

    def power_limited_acceleration(
        self, ctx: Context, velocity: float
    ) -> float:

        drive_force = self.powertrain.drive_force(ctx, velocity)
        resistive_fx = sum(self.resistive_forces(ctx, velocity))
        net_force = drive_force - resistive_fx
        return net_force / ctx.vehicle.equivalent_mass

    ###############################################
    # Time is running out

    def resolve_vehicle_state(
        self, ctx: Context, velocity: float
    ) -> FullVehicleState:
        """
        Calculate the full state of the vehicle at a node.

        Args:
            ctx (Context): The simulation context.
            velocity (float): The vehicle's velocity.

        Returns:
            vehicle_state (FullVehicleState): The full state of the vehicle,
                including forces, torques, and energy.
        """

        weight = ctx.vehicle.total_mass * ctx.environment.gravity
        centripetal_force = (
            ctx.vehicle.total_mass * velocity**2 * ctx.node.curvature
        )

        aero_attitude = AeroAttitude(
            velocity=velocity, air_density=ctx.environment.air_density
        )
        downforce = ctx.vehicle.aero.get_downforce(aero_attitude)
        drag = ctx.vehicle.aero.get_drag(aero_attitude)

        resistive_fx = drag + ctx.node.z_to_x(weight)
        required_fy = ctx.node.y_to_y(centripetal_force) + ctx.node.z_to_y(
            weight
        )
        normal_force = (
            ctx.node.z_to_z(weight)
            + ctx.node.y_to_z(centripetal_force)
            + downforce
        )

        # normal_loads = self.get_normal_loads(normal_force)
        # tyre_attitudes = self.get_tyre_attitudes(normal_loads)
        # lateral_traction = self.get_lateral_traction(
        #     ctx, tyre_attitudes, resistive_fx
        # )
        # longitudinal_traction = self.get_longitudinal_traction(
        #     ctx, tyre_attitudes, required_fy
        # )

        motor_speed = ctx.vehicle.velocity_to_motor_speed(velocity)
        motor_torque = ctx.vehicle.powertrain.get_motor_torque(
            state_of_charge=ctx.state.state_of_charge, motor_speed=motor_speed
        )
        motor_power = motor_speed * motor_torque
        accumulator_power = ctx.vehicle.powertrain.motor_to_accumulator_power(
            motor_power
        )
        motor_force = ctx.vehicle.motor_torque_to_drive_force(motor_torque)

        return FullVehicleState(
            weight=weight,
            centripetal_force=centripetal_force,
            downforce=downforce,
            drag=drag,
            resistive_fx=resistive_fx,
            required_fy=required_fy,
            normal_force=normal_force,
            # normal_loads=normal_loads,
            # tyre_attitudes=tyre_attitudes,
            # lateral_traction=lateral_traction,
            # longitudinal_traction=longitudinal_traction,
            motor_speed=motor_speed,
            motor_torque=motor_torque,
            motor_power=motor_power,
            accumulator_power=accumulator_power,
            motor_force=motor_force,
        )

    # @abstractmethod
    # def get_normal_loads(self, normal_force: float) -> FourCorner[float]:
    #     pass

    # @abstractmethod
    # def get_tyre_attitudes(
    #     self, normal_loads: FourCorner[float]
    # ) -> FourCorner[TyreAttitude]:
    #     pass

    # @abstractmethod
    # def get_lateral_traction(
    #     self,
    #     ctx: Context,
    #     attitudes: FourCorner[TyreAttitude],
    #     required_fx: float,
    # ) -> FourCorner[float]:
    #     pass

    # @abstractmethod
    # def get_longitudinal_traction(
    #     self,
    #     ctx: Context,
    #     attitudes: FourCorner[TyreAttitude],
    #     required_fy: float,
    # ) -> FourCorner[float]:
    #     pass

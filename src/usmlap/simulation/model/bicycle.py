"""
This module defines the bicycle vehicle model.
"""

from usmlap.simulation.vehicle_state import StateVariables
from usmlap.track import TrackNode
from usmlap.utils.datatypes import FrontRear
from usmlap.vehicle.tyre import TyreAttitude

from ..errors import FailedToConvergeError, InsufficientTractionError
from .vehicle_model import VehicleModelInterface

PRECISION = 1e-3
MAXIMUM_ITERATIONS = 100


class BicycleVehicleModel(VehicleModelInterface):
    """
    Bicycle vehicle model.
    """

    def lateral_traction_limit(
        self, state_variables: StateVariables, node: TrackNode, velocity: float
    ) -> float:
        weight = self.weight()
        drag = self.drag(velocity)
        resistive_fx = drag + node.z_to_x(weight)

        centripetal_force = self.centripetal_force(node, velocity)
        downforce = self.downforce(velocity)
        effective_weight = weight + node.y_to_z(centripetal_force)
        normal_loads = self._get_normal_loads(effective_weight, downforce, 0)
        # No longitudinal acceleration, therefore no load transfer

        front_tyre = self.vehicle.tyres.front.tyre_model
        front_attitude = TyreAttitude(normal_loads.front / 2)
        front_traction = 2 * front_tyre.calculate_lateral_force(
            front_attitude, required_fx=0
        )

        try:
            rear_tyre = self.vehicle.tyres.rear.tyre_model
            rear_attitude = TyreAttitude(normal_loads.rear / 2)
            rear_traction = 2 * rear_tyre.calculate_lateral_force(
                rear_attitude, required_fx=resistive_fx / 2
            )
        except ValueError:
            raise InsufficientTractionError(required_traction=resistive_fx)

        traction_limit = front_traction + rear_traction
        return traction_limit

    def traction_limited_acceleration(
        self, state_variables: StateVariables, node: TrackNode, velocity: float
    ) -> float:

        weight = self.weight()
        resistive_fx = self.resistive_fx(node, velocity)
        centripetal_force = self.centripetal_force(node, velocity)
        required_fy = centripetal_force + node.z_to_y(weight)

        downforce = self.downforce(velocity)

        accelerations: list[float] = [0]
        residuals: list[float] = []

        for _ in range(MAXIMUM_ITERATIONS):
            load_transfer = self.vehicle.long_load_transfer(accelerations[-1])
            normal_loads = self._get_normal_loads(
                weight, downforce, load_transfer
            )
            try:
                front_tyre = self.vehicle.tyres.front.tyre_model
                front_attitude = TyreAttitude(normal_loads.front / 2)
                _ = front_tyre.calculate_longitudinal_force(
                    front_attitude, abs(required_fy / 4)
                )

                rear_tyre = self.vehicle.tyres.rear.tyre_model
                rear_attitude = TyreAttitude(normal_loads.rear / 2)
                rear_traction = 2 * rear_tyre.calculate_longitudinal_force(
                    rear_attitude, abs(required_fy / 4)
                )

            except ValueError:
                raise InsufficientTractionError(required_traction=required_fy)

            net_force = rear_traction - resistive_fx
            accelerations.append(net_force / self.vehicle.equivalent_mass)
            residuals.append(accelerations[-1] - accelerations[-2])
            if abs(residuals[-1]) < PRECISION:
                return accelerations[-1]

        raise FailedToConvergeError(MAXIMUM_ITERATIONS, residuals)

    def traction_limited_braking(
        self, state_variables: StateVariables, node: TrackNode, velocity: float
    ) -> float:

        weight = self.weight()
        resistive_fx = self.resistive_fx(node, velocity)
        centripetal_force = self.centripetal_force(node, velocity)
        required_fy = centripetal_force + node.z_to_y(weight)

        downforce = self.downforce(velocity)

        accelerations: list[float] = [0]
        residuals: list[float] = []

        for _ in range(MAXIMUM_ITERATIONS):
            load_transfer = self.vehicle.long_load_transfer(accelerations[-1])
            normal_loads = self._get_normal_loads(
                weight, downforce, load_transfer
            )
            try:
                front_tyre = self.vehicle.tyres.front.tyre_model
                front_attitude = TyreAttitude(normal_loads.front / 2)
                front_traction = front_tyre.calculate_longitudinal_force(
                    front_attitude, abs(required_fy / 4)
                )

                rear_tyre = self.vehicle.tyres.rear.tyre_model
                rear_attitude = TyreAttitude(normal_loads.rear / 2)
                rear_traction = 2 * rear_tyre.calculate_longitudinal_force(
                    rear_attitude, abs(required_fy / 4)
                )

            except ValueError:
                raise InsufficientTractionError(required_traction=required_fy)

            net_force = -front_traction - rear_traction - resistive_fx
            accelerations.append(net_force / self.vehicle.equivalent_mass)
            residuals.append(accelerations[-1] - accelerations[-2])
            if abs(residuals[-1]) < PRECISION:
                return accelerations[-1]

        raise FailedToConvergeError(MAXIMUM_ITERATIONS, residuals)

    def _get_normal_loads(
        self, weight: float, downforce: float, load_transfer: float
    ) -> FrontRear[float]:
        split_weight = self.vehicle.mass_distribution * weight
        split_downforce = self.vehicle.aero_distribution * downforce
        split_load_transfer = FrontRear(load_transfer, -load_transfer)
        normal_loads = split_weight + split_downforce + split_load_transfer
        return normal_loads

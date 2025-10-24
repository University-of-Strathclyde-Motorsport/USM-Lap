"""
This module contains code for running a simulation.
"""

import math
from pydantic import BaseModel, ConfigDict
from vehicle.vehicle import Vehicle
from vehicle.aero import AeroAttitude
from vehicle.tyre.tyre_model import TyreAttitude
from track.mesh import Mesh, Node
from .environment import Environment
from .model.point_mass import PointMassVehicleModel
from .solver.quasi_steady_state import QuasiSteadyStateSolver


class Simulation(BaseModel):
    """
    A simulation object.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    vehicle: Vehicle
    track: Mesh
    environment: Environment = Environment()
    vehicle_model: PointMassVehicleModel = PointMassVehicleModel()
    solver: QuasiSteadyStateSolver = QuasiSteadyStateSolver()

    def solve(self) -> list[float]:
        maximum_speed: list[float] = []
        for node in self.track.nodes:
            maximum_speed.append(self.lateral_vehicle_model(node))
        return maximum_speed

    def lateral_vehicle_model(self, node: Node) -> float:
        print(f"Node: {node}")
        if node.curvature == 0:
            return 100  # Vehicle maximum speed

        # Weight
        weight = self.vehicle.total_mass * self.environment.gravity
        weight_z = weight * math.cos(node.banking) * math.cos(node.inclination)
        weight_y = -weight * math.sin(node.banking)
        weight_x = weight * math.sin(node.inclination)

        print(f"Weight: {weight}, X: {weight_x}, Y: {weight_y}, Z: {weight_z}")

        # Initial speed solution
        v = self.vehicle.maximum_velocity  # Improve initial guess
        i = 0

        # Calculate forces
        while i < 10000:
            i += 1
            print(f"Iteration {i}, velocity = {v}")
            aero_attitude = AeroAttitude(velocity=v)
            downforce = self.vehicle.aero.get_downforce(aero_attitude)
            drag = self.vehicle.aero.get_drag(aero_attitude)
            # Rolling resistance
            normal_load = (weight_z + downforce) / 4

            print(
                f"Downforce: {downforce}, Drag: {drag}, Normal load: {normal_load}"
            )

            tyre_attitude = TyreAttitude(normal_load=normal_load)
            required_fx = drag + weight_x
            required_fy = self.vehicle.total_mass * abs(
                v**2 * node.curvature
                + (self.environment.gravity * math.sin(node.banking))
            )
            try:
                available_fy = (
                    self.vehicle.tyres.front.tyre_model.calculate_lateral_force(
                        tyre_attitude, required_fx / 4
                    )
                ) * 4
            except ValueError:
                available_fy = 0

            print(f"Required fx: {required_fx}, fy: {required_fy}")
            print(f"Available fy: {available_fy}")

            if available_fy < required_fy:
                ay = (available_fy + weight_y) / self.vehicle.total_mass
                v = math.sqrt(ay / abs(node.curvature)) - 0.001
            else:
                break

        print(f"Converged after {i} iterations")
        return v

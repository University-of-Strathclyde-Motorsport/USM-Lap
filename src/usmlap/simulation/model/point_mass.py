"""
This module defines the point mass vehicle model.
"""

import math
from vehicle.vehicle import Vehicle
from simulation.environment import Environment
from track.mesh import Node
from .vehicle_model import VehicleModelInterface, VehicleState
from vehicle.aero import AeroAttitude
from vehicle.tyre.tyre_model import TyreAttitude


class PointMassVehicleModel(VehicleModelInterface):
    """
    Point mass vehicle model.
    """

    def lateral_vehicle_model(
        self, vehicle: Vehicle, environment: Environment, node: Node
    ) -> VehicleState:
        weight = vehicle.total_mass * environment.gravity
        weight_z = weight * math.cos(node.banking) * math.cos(node.inclination)
        weight_y = -weight * math.sin(node.banking)
        weight_x = weight * math.sin(node.inclination)

        v = vehicle.maximum_velocity
        i = 0

        while i < 10000:
            i += 1

            # Aero forces
            aero_attitude = AeroAttitude(velocity=v)
            downforce = vehicle.aero.get_downforce(aero_attitude)
            drag = vehicle.aero.get_drag(aero_attitude)
            normal_load = (weight_z + downforce) / 4

            required_fx = drag + weight_x
            centripetal_force = vehicle.total_mass * v**2 * node.curvature
            required_fy = abs(weight_y + centripetal_force)

            tyre_attitude = TyreAttitude(normal_load=normal_load)
            try:
                available_fy = (
                    vehicle.tyres.front.tyre_model.calculate_lateral_force(
                        tyre_attitude, required_fx / 4
                    )
                ) * 4
            except ValueError:
                available_fy = 0

            if available_fy < required_fy:
                ay = (available_fy + weight_y) / vehicle.total_mass
                v = math.sqrt(ay / abs(node.curvature)) - 0.001
            else:
                break

        return VehicleState(velocity=v, ax=0)

    def calculate_acceleration(
        self,
        vehicle: Vehicle,
        environment: Environment,
        node: Node,
        velocity: float,
    ) -> float:
        weight = vehicle.total_mass * environment.gravity
        weight_z = weight * math.cos(node.banking) * math.cos(node.inclination)
        weight_y = -weight * math.sin(node.banking)
        weight_x = weight * math.sin(node.inclination)

        centripetal_force = vehicle.total_mass * velocity**2 * node.curvature
        required_fy = abs(weight_y + centripetal_force)

        aero_attitude = AeroAttitude(velocity=velocity)
        downforce = vehicle.aero.get_downforce(aero_attitude)
        drag = vehicle.aero.get_drag(aero_attitude)
        normal_load = (weight_z + downforce) / 4

        tyre_attitude = TyreAttitude(normal_load=normal_load)
        traction_fx = (
            vehicle.tyres.front.tyre_model.calculate_longitudinal_force(
                tyre_attitude, required_fy / 4
            )
            * 4
        )
        resistive_fx = drag + weight_x
        net_fx = traction_fx - resistive_fx
        return net_fx / vehicle.equivalent_mass

    def calculate_braking(
        self,
        vehicle: Vehicle,
        environment: Environment,
        node: Node,
        velocity: float,
    ) -> float:
        weight = vehicle.total_mass * environment.gravity
        weight_z = weight * math.cos(node.banking) * math.cos(node.inclination)
        weight_y = -weight * math.sin(node.banking)
        weight_x = weight * math.sin(node.inclination)

        centripetal_force = vehicle.total_mass * velocity**2 * node.curvature
        required_fy = abs(weight_y + centripetal_force)

        aero_attitude = AeroAttitude(velocity=velocity)
        downforce = vehicle.aero.get_downforce(aero_attitude)
        drag = vehicle.aero.get_drag(aero_attitude)
        normal_load = (weight_z + downforce) / 4

        tyre_attitude = TyreAttitude(normal_load=normal_load)
        traction_fx = (
            vehicle.tyres.front.tyre_model.calculate_longitudinal_force(
                tyre_attitude, required_fy / 4
            )
            * 4
        )
        resistive_fx = drag + weight_x
        net_fx = traction_fx + resistive_fx
        return net_fx / vehicle.equivalent_mass

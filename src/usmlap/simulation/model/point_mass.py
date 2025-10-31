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
            aero_attitude = AeroAttitude(
                velocity=v, air_density=environment.air_density
            )
            downforce = vehicle.aero.get_downforce(aero_attitude)
            drag = vehicle.aero.get_drag(aero_attitude)
            normal_load = (weight_z + downforce) / 4

            required_fx = drag + weight_x
            centripetal_force = vehicle.total_mass * v**2 * node.curvature
            required_fy = abs(weight_y + centripetal_force)

            tyre_attitude = TyreAttitude(normal_load=normal_load)
            try:
                fy_front = (
                    vehicle.tyres.front.tyre_model.calculate_lateral_force(
                        tyre_attitude, required_fx=0
                    )
                )
                fy_rear = (
                    vehicle.tyres.front.tyre_model.calculate_lateral_force(
                        tyre_attitude, required_fx / 2
                    )
                )
                available_fy = 2 * (fy_front + fy_rear)
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

        aero_attitude = AeroAttitude(
            velocity=velocity, air_density=environment.air_density
        )
        downforce = vehicle.aero.get_downforce(aero_attitude)
        drag = vehicle.aero.get_drag(aero_attitude)
        normal_load = (weight_z + downforce) / 4

        tyre_attitude = TyreAttitude(normal_load=normal_load)
        traction_limit_fx = (
            vehicle.tyres.front.tyre_model.calculate_longitudinal_force(
                tyre_attitude, required_fy / 4
            )
            * 2
        )
        motor_limit_fx = self.get_drive_force(vehicle, velocity)
        drive_fx = min(motor_limit_fx, traction_limit_fx)
        resistive_fx = drag + weight_x
        net_fx = drive_fx - resistive_fx
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

        aero_attitude = AeroAttitude(
            velocity=velocity, air_density=environment.air_density
        )
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

    def get_motor_power(self, vehicle: Vehicle, velocity: float) -> float:
        motor_speed = vehicle.velocity_to_motor_speed(velocity)
        power = vehicle.powertrain.get_motor_power(
            state_of_charge=1, current=0, motor_speed=motor_speed
        )
        return power

    def get_drive_force(self, vehicle: Vehicle, velocity: float) -> float:
        motor_speed = vehicle.velocity_to_motor_speed(velocity)
        motor_torque = vehicle.powertrain.get_motor_torque(
            state_of_charge=1,
            current=vehicle.powertrain.accumulator.maximum_discharge_current,
            motor_speed=motor_speed,
        )
        drive_force = vehicle.motor_torque_to_drive_force(motor_torque)
        print(
            f"Velocity: {velocity}, speed: {motor_speed}, torque: {motor_torque}, force: {drive_force}"
        )
        return drive_force

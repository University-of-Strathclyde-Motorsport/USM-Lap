from vehicle.vehicle import Vehicle
from track.mesh import MeshGenerator
from track.track_data import TrackData
from simulation.simulation import Simulation
from simulation.environment import Environment
from simulation.model.point_mass import PointMassVehicleModel
from simulation.solver.quasi_steady_state import QuasiSteadyStateSolver
import matplotlib.pyplot as plt

root = "D:/Repositories/USM-Lap/appdata/library/"

vehicle_file = root + "vehicles/USM23 Baseline.json"
vehicle = Vehicle.from_json(vehicle_file)

model = PointMassVehicleModel()
velocity = range(0, 50)
force = [model.get_drive_force(vehicle, v) for v in velocity]
plt.plot(velocity, force)

track_file = root + "tracks/FS AutoX Germany 2012.xlsx"
track_data = TrackData.load_track_from_spreadsheet(track_file)
mesh = MeshGenerator(resolution=1).generate_mesh(track_data)

simulation = Simulation(
    vehicle=vehicle,
    track=mesh,
    environment=Environment(),
    vehicle_model=PointMassVehicleModel(),
    solver=QuasiSteadyStateSolver(),
)

solution = simulation.solve()
solution.plot_apexes()

print(f"Time: {solution.total_time} s")
print(f"Average velocity: {solution.average_velocity} m/s")

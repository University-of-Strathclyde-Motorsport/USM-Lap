from vehicle.vehicle import Vehicle
from vehicle.parameters import Parameter
from track.track_data import TrackData
from track.mesh import MeshGenerator
from simulation.simulation import SimulationSettings
from analysis.sweep_1d import sweep_1d, SweepSettings

root = "D:/Repositories/USM-Lap/appdata/library/"

vehicle_file = root + "vehicles/USM23 Baseline.json"
vehicle = Vehicle.from_json(vehicle_file)

track_file = root + "tracks/FS AutoX Germany 2012.xlsx"
track_data = TrackData.load_track_from_spreadsheet(track_file)
mesh = MeshGenerator(resolution=1).generate_mesh(track_data)

settings = SimulationSettings(track=mesh)

sweep_settings = SweepSettings(
    parameter=Parameter.get_parameter("Curb Mass"),
    start_value=200,
    end_value=250,
    number_of_steps=5,
)
sweep_results = sweep_1d(
    baseline_vehicle=vehicle,
    sweep_settings=sweep_settings,
    simulation_settings=settings,
)
sweep_results.plot()

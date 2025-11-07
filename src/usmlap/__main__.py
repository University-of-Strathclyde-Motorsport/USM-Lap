from vehicle.vehicle import Vehicle
import vehicle.parameters as parameters
from track.track_data import TrackData
from track.mesh import MeshGenerator
from simulation.simulation import SimulationSettings
from simulation.sensitivity import SensitivityAnalysis

root = "D:/Repositories/USM-Lap/appdata/library/"

vehicle_file = root + "vehicles/USM23 Baseline.json"
vehicle = Vehicle.from_json(vehicle_file)

track_file = root + "tracks/FS AutoX Germany 2012.xlsx"
track_data = TrackData.load_track_from_spreadsheet(track_file)
mesh = MeshGenerator(resolution=1).generate_mesh(track_data)

settings = SimulationSettings(track=mesh)

sensitivity_analysis = SensitivityAnalysis(
    baseline_vehicle=vehicle,
    parameter=parameters.CurbMass(),
    simulation_settings=settings,
)

sensitivity = sensitivity_analysis.get_sensitivity()
print(f"Sensitivity: {sensitivity:.4f}")

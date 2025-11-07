from vehicle.vehicle import Vehicle
import vehicle.parameters as parameters
from simulation.sensitivity import SensitivityAnalysis

root = "D:/Repositories/USM-Lap/appdata/library/"

vehicle_file = root + "vehicles/USM23 Baseline.json"
vehicle = Vehicle.from_json(vehicle_file)

track_file = root + "tracks/FS AutoX Germany 2012.xlsx"

sensitivity_analysis = SensitivityAnalysis(
    baseline_vehicle=vehicle, parameter=parameters.CurbMass()
)

sensitivity = sensitivity_analysis.get_sensitivity()
print(f"Sensitivity: {sensitivity:.4f}")

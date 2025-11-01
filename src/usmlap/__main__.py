from vehicle.vehicle import Vehicle
from simulation.competition import Competition

root = "D:/Repositories/USM-Lap/appdata/library/"

vehicle_file = root + "vehicles/USM23 Baseline.json"
vehicle = Vehicle.from_json(vehicle_file)

track_file = root + "tracks/FS AutoX Germany 2012.xlsx"

competition = Competition(vehicle=vehicle, autocross_track=track_file)

solution = competition.simulate()

print("Results:")
print(f"Acceleration: {solution.acceleration.total_time} s")
print(f"Skidpad: {solution.skidpad.total_time} s")
print(f"Autocross: {solution.autocross.total_time} s")
print(f"Endurance: {solution.endurance.total_time} s")

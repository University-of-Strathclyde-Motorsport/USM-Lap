from vehicle.vehicle import Vehicle
from simulation.competition import Competition
from simulation.points.points_calculator import PointsCalculator

root = "D:/Repositories/USM-Lap/appdata/library/"

vehicle_file = root + "vehicles/USM23 Baseline.json"
vehicle = Vehicle.from_json(vehicle_file)

track_file = root + "tracks/FS AutoX Germany 2012.xlsx"

competition = Competition(vehicle=vehicle, autocross_track=track_file)

results = competition.simulate()

print("Results:")
print(f"Acceleration: {results.acceleration.total_time} s")
print(f"Skidpad: {results.skidpad.total_time} s")
print(f"Autocross: {results.autocross.total_time} s")
print(f"Endurance: {results.endurance.total_time} s")

points_calculator = PointsCalculator(competition_results=results)
points_calculator.plot_pie_chart()
# print(f"Total points: {points_calculator.total_points}")

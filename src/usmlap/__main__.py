from vehicle.vehicle import Vehicle

root = "D:/Repositories/USM-Lap/appdata/library/vehicles/"
filename = "USM23 Baseline.json"

vehicle = Vehicle.from_json(root + filename)
print(vehicle)

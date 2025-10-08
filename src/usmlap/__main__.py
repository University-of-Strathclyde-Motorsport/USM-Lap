from vehicle.vehicle import Vehicle
from vehicle.suspension import SuspensionAxle

root = "D:/Repositories/USM-Lap/appdata/library/vehicles/"
filename = "USM23 Baseline.json"

vehicle = Vehicle.from_json(root + filename)
print(vehicle)
print(vehicle.suspension.front.implementation_name())

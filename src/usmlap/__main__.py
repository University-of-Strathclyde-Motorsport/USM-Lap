from vehicle.vehicle import Vehicle

root = "D:/Repositories/USM-Lap/appdata/library/vehicles/"
filename = "USM23 Baseline.json"

print()
vehicle = Vehicle.from_json(root + filename)
print(vehicle)
print(f"Front suspension: {type(vehicle.suspension.front).__name__}")
print(vehicle.suspension.front.to_json())
print(f"Rear suspension: {type(vehicle.suspension.rear).__name__}")
print(vehicle.suspension.rear.to_json())

print(SuspensionAxle.get_subtype_dictionary())

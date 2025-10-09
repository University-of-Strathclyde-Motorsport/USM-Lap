from vehicle.vehicle import Vehicle

root = "D:/Repositories/USM-Lap/appdata/library/vehicles/"
filename = "USM23 Baseline.json"

vehicle = Vehicle.from_json(root + filename)
print(vehicle.to_json())
print(f"Front suspension: {type(vehicle.suspension.front).__name__}")
print(vehicle.suspension.front.to_json())
print(f"Rear suspension: {type(vehicle.suspension.rear).__name__}")
print(vehicle.suspension.rear.to_json())
print(
    f"Tyres: {type(vehicle.tyres.front).__name__}, {type(vehicle.tyres.rear).__name__}"
)
print(vehicle.tyres.front.to_json())
print(vehicle.tyres.rear.to_json())

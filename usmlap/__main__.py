from vehicle import brakes

brakes = brakes.Brakes.from_json("library/vehicles/USM23_baseline.json")
print(brakes)
print(brakes.brake_lines)

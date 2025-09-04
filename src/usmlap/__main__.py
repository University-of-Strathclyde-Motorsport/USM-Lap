from vehicle import brakes


brakes = brakes.Brakes.from_json(
    "appdata/library/vehicles/USM23_baseline copy.json"
)
print(type(brakes))
print(type(brakes.front))

print(brakes.pedal_force_to_wheel_torque(2000))
print(brakes.get_overall_brake_balance())

print(brakes.to_json())

from vehicle import brakes, transmission

t = transmission.Transmission(
    primary_gear_reduction=1, final_gear_reduction=1, gear_ratio=[4]
)
print(t.to_json())
print(t.overall_gear_ratio)


# brakes = brakes.Brakes.from_json(
#     "appdata/library/vehicles/USM23_baseline copy.json"
# )
# print(type(brakes))
# print(type(brakes.front))

# print(brakes.pedal_force_to_wheel_torque(2000))
# print(brakes.get_overall_brake_balance())

# print(brakes.to_json())

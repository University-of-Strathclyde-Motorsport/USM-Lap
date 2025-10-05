from vehicle.powertrain import motor

M = motor.Motor.from_library("EMRAX 228")
print(M)
for i in range(0, 1000, 100):
    print(M.get_power(i))

M.plot_power_curve()

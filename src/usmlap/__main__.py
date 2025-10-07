from vehicle.powertrain import accumulator, motor, motor_controller, powertrain

C = accumulator.Cell.from_library("Molicel P30B")
A = accumulator.Accumulator(cell=C, cells_in_parallel=6, cells_in_series=112)
M = motor.Motor.from_library("EMRAX 228")
MC = motor_controller.MotorController.from_library("BAMOCAR")
PT = powertrain.RWDPowertrain(A, M, MC)

PT.plot_motor_curve(state_of_charge=0)

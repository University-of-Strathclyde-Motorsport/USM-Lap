from vehicle.powertrain.powertrain import RWDPowertrain
from vehicle.powertrain.accumulator import Cell

root = "D:/Repositories/USM-Lap/appdata/library/vehicles/"
# filename = "powertrain.json"
filename = "powertrain_names.json"
powertrain = RWDPowertrain.from_json(root + filename)
print(powertrain)

cell = Cell.from_library("Molicel P30b")
print(cell)

print(Cell.load_library())

# A = accumulator.Accumulator(cell=C, cells_in_parallel=6, cells_in_series=112)
# M = motor.Motor.from_library("EMRAX 228")
# MC = motor_controller.MotorController.from_library("BAMOCAR")
# PT = powertrain.RWDPowertrain(A, M, MC)

# PT.plot_motor_curve(state_of_charge=0)

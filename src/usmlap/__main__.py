from vehicle.tyre import tir


tir_params = tir.TIRParameters.from_file(
    "appdata/library/tyres/HS R25B 16x75 10x7/MF612.tir"
)

print(tir_params)

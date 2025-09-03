from vehicle import brakes


cylinder = brakes.MasterCylinder()
cylinder.piston_diameter = 0.1
cylinder_json = cylinder.to_json()
print(cylinder_json)

new_cylinder = brakes.MasterCylinder.from_json(cylinder_json)
print(new_cylinder.to_json())
cylinder.piston_diameter = 0.2

line = brakes.BrakeLine(cylinder=new_cylinder)
line_json = line.to_json()
print(line_json)

line_new = brakes.BrakeLine.from_json(line_json)
print(line_new.to_json())

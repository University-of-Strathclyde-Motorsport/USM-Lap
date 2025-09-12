from track.track_data import TrackData, GripFactorData
from track.mesh import MeshGenerator
from utils.array import diff

filepath = "appdata/library/tracks/Spa-Francorchamps.xlsx"
td = TrackData.load_track_from_spreadsheet(filepath)
print(td)

mg = MeshGenerator()
mesh = mg.generate_mesh(td)
print(mesh)

node_length = [node.length for node in mesh.nodes]
diff_pos = diff([node.position for node in mesh.nodes])

delta = [node_length[i] - diff_pos[i] for i in range(len(diff_pos))]
print(delta)
print(max(delta))
print(mesh.nodes[-1].position)


ld = GripFactorData([1, 2, 3], [0.1, 5, 6])
print(ld)
print(ld[2])
print(ld[-2])
print(ld[0:3])
print(len(ld))
print(min(ld))
print(ld.interpolate([0, 1.5, 2.5, 3.5]))

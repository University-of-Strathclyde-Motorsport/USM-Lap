from track import track_data, mesh
from utils.array import diff

filepath = "appdata/library/tracks/FS AutoX Germany 2012.xlsx"
td = track_data.TrackData.load_track_from_spreadsheet(filepath)
print(td)

mg = mesh.MeshGenerator()
mesh = mg.generate_mesh(td)
print(mesh)

node_length = [node.length for node in mesh.nodes]
diff_pos = diff([node.position for node in mesh.nodes])

delta = [node_length[i] - diff_pos[i] for i in range(len(diff_pos))]
print(delta)
print(max(delta))
print(mesh.nodes[-1].position)

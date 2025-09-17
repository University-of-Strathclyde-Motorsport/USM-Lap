from track.track_data import TrackData
from track.mesh import MeshGenerator
import statistics


filepath = "appdata/library/tracks/Spa-Francorchamps.xlsx"
# params = TIRParameters.from_file(
#     "appdata/library/tyres/HS R25B 16x75 10x7/MF612.tir"
# )

td = TrackData.load_track_from_spreadsheet(filepath)
print(td)

mg = MeshGenerator(resolution=1)
print(mg)

mesh = mg.generate_mesh(td)
print(mesh)

lengths = [node.length for node in mesh.nodes]
print(max(lengths))
print(min(lengths))

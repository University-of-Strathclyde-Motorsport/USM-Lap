"""
This script plots a map of a track.
"""

from dataclasses import dataclass

import matplotlib.pyplot as plt

from usmlap.plot import plot_map
from usmlap.plot.style import USM_BLUE, USM_LIGHT_BLUE, USM_ORANGE
from usmlap.track import TrackData, generate_mesh

TRACK_SHEET = "FS AutoX Germany 2012"
MESH_RESOLUTION = 0.1


@dataclass
class MeshConfiguration(object):
    """Configuration details for generating and plotting a track mesh."""

    label: str
    colour: str
    correct_tangency: bool
    correct_displacement: bool


configurations: list[MeshConfiguration] = [
    MeshConfiguration("Uncorrected Mesh", USM_ORANGE, False, False),
    MeshConfiguration("Tangency Correction", USM_LIGHT_BLUE, True, False),
    MeshConfiguration("Displacement Correction", USM_BLUE, True, True),
]

_, ax = plt.subplots()
track_data = TrackData.from_json(TRACK_SHEET)

# for config in configurations:
#     mesh = generate_mesh(
#         track_data,
#         resolution=MESH_RESOLUTION,
#         correct_tangency=config.correct_tangency,
#         correct_displacement=config.correct_displacement,
#     )
#     ax = plot_map(
#         mesh, ax, colour=config.colour, label=config.label, show_legend=True
#     )

mesh = generate_mesh(
    track_data,
    resolution=MESH_RESOLUTION,
    correct_tangency=True,
    correct_displacement=True,
)
plot_map(mesh, ax, colour=USM_BLUE)

plt.show()

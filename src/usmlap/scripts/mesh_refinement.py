"""
This script runs a mesh refinement simulation.

A vehicle is simulated over a range of track mesh resolutions.
The laptime and computation time for each simulation
are plotted against the resolution.
"""

import time
from dataclasses import dataclass

import matplotlib.pyplot as plt

from usmlap.plot.utils import combined_legend
from usmlap.simulation.simulation import SimulationSettings, simulate
from usmlap.simulation.solver.quasi_transient import QuasiTransientSolver
from usmlap.track.mesh import MeshGenerator
from usmlap.track.track_data import load_track_from_spreadsheet
from usmlap.vehicle.vehicle import load_vehicle

RESOLUTIONS = [10, 5, 2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005]
TRACK_SHEET = "FS AutoX Germany 2012.xlsx"
VEHICLE = "USM23 Baseline.json"
SOLVER = QuasiTransientSolver


@dataclass
class MeshRefinementResult(object):
    """Mesh refinement result."""

    track_length: float
    resolution: float
    node_count: int
    laptime: float
    mesh_time: float
    simulation_time: float

    @property
    def total_time(self) -> float:
        return self.mesh_time + self.simulation_time


def mesh_refinement() -> list[MeshRefinementResult]:
    """Run a mesh refinement simulation."""

    track_data = load_track_from_spreadsheet(TRACK_SHEET)
    vehicle = load_vehicle(VEHICLE)
    simulation_settings = SimulationSettings(solver=SOLVER)

    mesh_refinement_results: list[MeshRefinementResult] = []

    for resolution in RESOLUTIONS:
        mesh_start_time = time.time()
        mesh = MeshGenerator(resolution=resolution).generate_mesh(track_data)
        mesh_time = time.time() - mesh_start_time

        simulation_start_time = time.time()
        results = simulate(vehicle, mesh, simulation_settings)
        simulation_time = time.time() - simulation_start_time

        mesh_refinement_results.append(
            MeshRefinementResult(
                track_length=mesh.track_length,
                resolution=resolution,
                node_count=mesh.node_count,
                laptime=results.total_time,
                mesh_time=mesh_time,
                simulation_time=simulation_time,
            )
        )

    return mesh_refinement_results


def plot_mesh_refinement(results: list[MeshRefinementResult]) -> None:
    """Plot metrics from a mesh refinement simulation."""

    resolutions = [result.resolution for result in results]
    node_counts = [result.node_count for result in results]
    laptimes = [result.laptime for result in results]
    mesh_times = [result.mesh_time for result in results]
    simulation_times = [result.simulation_time for result in results]

    _, ax_laptime = plt.subplots()
    ax_comptime = ax_laptime.twinx()

    ax_laptime.xaxis.set_inverted(True)
    ax_laptime.set_xscale("log")
    ax_laptime.set_xticks(resolutions)
    ax_laptime.set_xticklabels(resolutions)
    ax_laptime.set_xlim(max(resolutions), min(resolutions))

    ax_nodes = ax_laptime.twiny()
    ax_nodes.xaxis.set_inverted(True)
    ax_nodes.set_xscale("log")
    ax_nodes.set_xticks(resolutions)
    ax_nodes.set_xticklabels(node_counts)
    ax_nodes.set_xlim(max(resolutions), min(resolutions))

    ax_laptime.plot(resolutions, laptimes, color="#003366", label="Laptime")

    ax_comptime.stackplot(
        resolutions,
        mesh_times,
        simulation_times,
        colors=["#69C2CD", "#FD9055"],
        labels=["Mesh Generation", "Simulation"],
    )

    ax_laptime.set_zorder(ax_comptime.get_zorder() + 1)
    ax_laptime.patch.set_visible(False)  # type: ignore

    ax_laptime.set_xlabel("Resolution (m)")
    ax_nodes.set_xlabel("Node Count")
    ax_laptime.set_ylabel("Calculated Laptime (s)")
    ax_comptime.set_ylabel("Computation Time (s)")
    plt.suptitle("Mesh Refinement")

    ax_laptime.grid()
    combined_legend(ax_laptime, ax_comptime)
    plt.tight_layout()
    plt.show()


def main() -> None:
    """Main function."""
    results = mesh_refinement()
    plot_mesh_refinement(results)


if __name__ == "__main__":
    main()

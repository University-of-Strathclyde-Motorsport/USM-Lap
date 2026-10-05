"""
This package implements algorithms for solving a vehicle's trajectory.
"""

from usmlap.core.registry import Registry

from .qss import QuasiSteadyStateSolver as QuasiSteadyStateSolver
from .qt import QuasiTransientSolver as QuasiTransientSolver
from .solution import Solution as Solution
from .solution import SolutionNode as SolutionNode
from .solver_interface import SolverInterface as SolverInterface

SolverRegistry = Registry[str, type[SolverInterface]]()
SolverRegistry.register("quasi-steady-state", QuasiSteadyStateSolver)
SolverRegistry.register("quasi-transient", QuasiTransientSolver)

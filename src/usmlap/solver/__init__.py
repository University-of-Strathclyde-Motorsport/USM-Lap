"""
This package implements algorithms for solving a vehicle's trajectory.
"""

from usmlap.core.registry import Registry
from usmlap.solver.qss.quasi_steady_state import QuasiSteadyStateSolver
from usmlap.solver.qt.quasi_transient import QuasiTransientSolver
from usmlap.solver.solver_interface import SolverInterface

SolverRegistry = Registry[str, type[SolverInterface]]()
SolverRegistry.register("quasi-steady-state", QuasiSteadyStateSolver)
SolverRegistry.register("quasi-transient", QuasiTransientSolver)

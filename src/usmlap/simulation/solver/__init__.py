"""
This subpackage contains solver implementations for laptime simulation.
"""

from .acceleration import calculate_next_velocity as calculate_next_velocity
from .apex_velocity import solve_apex_velocity as solve_apex_velocity
from .braking import calculate_initial_velocity as calculate_initial_velocity
from .quasi_steady_state import QuasiSteadyStateSolver as QuasiSteadyStateSolver
from .quasi_transient import QuasiTransientSolver as QuasiTransientSolver
from .solver_interface import SolverInterface as SolverInterface

"""
This module defines the context dataclass,
which stores all the information required by vehicle models.
"""

from dataclasses import dataclass

from usmlap.track import TrackNode
from usmlap.vehicle import Vehicle

from .environment import Environment
from .lambda_coefficients import LambdaCoefficients
from .vehicle_state import StateVariables


@dataclass
class Context(object):
    """
    Context object storing all the data required by vehicle models.

    Attributes:
        environment (Environment): Environmental variables for the simulation.
        vehicle (Vehicle): The vehicle being simulated.
        state (StateVariables): The vehicle's state variables.
        node (TrackNode): The track node to evaluate.
        lambdas (LambdaCoefficients): Lambda coefficients for the simulation.
    """

    environment: Environment
    vehicle: Vehicle
    state: StateVariables
    node: TrackNode
    lambdas: LambdaCoefficients

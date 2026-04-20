"""
This module defines the context dataclass,
which stores all the information required by vehicle models.
"""

from __future__ import annotations

from dataclasses import dataclass

from usmlap.track import TrackNode
from usmlap.vehicle import Vehicle

from .environment import Environment
from .lambda_coefficients import LambdaCoefficients
from .vehicle_state import TransientVariables


@dataclass
class GlobalContext(object):
    """
    Global context object storing data for an entire simulation.

    Attributes:
        environment (Environment): Environmental variables for the simulation.
        vehicle (Vehicle): The vehicle being simulated.
        lambdas (LambdaCoefficients): Lambda coefficients for the simulation.
    """

    environment: Environment
    vehicle: Vehicle
    lambdas: LambdaCoefficients

    def get_local_context(
        self, node: TrackNode, state: TransientVariables
    ) -> NodeContext:
        return NodeContext(
            environment=self.environment,
            vehicle=self.vehicle,
            state=state,
            node=node,
            lambdas=self.lambdas,
        )


@dataclass
class NodeContext(GlobalContext):
    """
    Context at a node of the track.

    Attributes:
        environment (Environment): Environmental variables for the simulation.
        vehicle (Vehicle): The vehicle being simulated.
        state (TransientVariables): The vehicle's state variables.
        node (TrackNode): The track node to evaluate.
        lambdas (LambdaCoefficients): Lambda coefficients for the simulation.
    """

    state: TransientVariables
    node: TrackNode

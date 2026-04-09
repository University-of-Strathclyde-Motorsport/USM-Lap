"""
This module defines custom error types for the simulation package.
"""


class SimulationError(Exception):
    """
    Base class for simulation errors.
    """


class InsufficientTractionError(SimulationError):
    """
    Error raised if the tyres cannot provide sufficient traction.
    """

    def __init__(self, required: float, available: float) -> None:
        super().__init__(
            f"Insufficient traction (required: {required:.1f}, available: {available:.1f})"
        )
        self.required = required
        self.availabe = available


class FailedToConvergeError(SimulationError):
    """
    Error raised if a solver fails to converge on a solution.
    """

    def __init__(self, iterations: int, residuals: list[float]) -> None:
        super().__init__(f"Failed to converge after {iterations} iterations")
        self.iterations = iterations
        self.residuals = residuals

    def plot(self) -> None:
        import matplotlib.pyplot as plt

        plt.plot(self.residuals)
        plt.xlabel("Iteration")
        plt.ylabel("Residual")
        plt.show()

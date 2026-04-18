"""
This module contains code for updating the vehicle state.
"""

from usmlap.model import FullVehicleState, NodeContext, StateVariables
from usmlap.model.errors import OutOfChargeError
from usmlap.vehicle.powertrain import StateOfCharge


def update_state_variables(
    ctx: NodeContext,
    initial_state: StateVariables,
    dt: float,
    vehicle_state: FullVehicleState,
) -> StateVariables:
    """Update the values of the transient variables."""

    soc = StateOfCharge(
        initial_state.state_of_charge + _discharge_rate(ctx, vehicle_state) * dt
    )
    if soc < 0:
        raise OutOfChargeError

    cell_temperature = initial_state.cell_temperature + (
        _temperature_rate(ctx, vehicle_state) * dt
    )

    return StateVariables(
        state_of_charge=soc, cell_temperature=cell_temperature
    )


def _discharge_rate(ctx: NodeContext, vehicle_state: FullVehicleState) -> float:
    """Rate of change of state of charge"""
    return (
        -vehicle_state.accumulator_current
        / ctx.vehicle.powertrain.accumulator.charge_capacity
    )


def _temperature_rate(
    ctx: NodeContext, vehicle_state: FullVehicleState
) -> float:
    """Rate of change of cell temperature."""
    thermal_mass = ctx.vehicle.powertrain.accumulator.thermal_mass
    net_power = vehicle_state.net_heating_power
    return net_power / thermal_mass

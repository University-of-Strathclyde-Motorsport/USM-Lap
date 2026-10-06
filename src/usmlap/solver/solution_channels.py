"""
This module implements telemetry channels for a solution.
"""

from __future__ import annotations

import logging
from enum import StrEnum

import numpy as np
import polars

from usmlap.core.types import Array1D
from usmlap.solver.solution import Solution
from usmlap.track.mesh import Mesh

logger = logging.getLogger(__name__)


class ChannelId(StrEnum):
    """Enumeration of telemetry channel ids."""

    S_LAP = "sLap"
    LENGTH = "length"
    RADIUS = "radius"
    CURVATURE = "curvature"
    ELEVATION = "elevation"
    INCLINATION = "inclination"
    BANKING = "banking"
    GRIP_FACTOR = "grip_factor"
    SECTOR = "sector"
    N_LAP = "nLap"
    HEADING_ANGLE = "heading_angle"
    V_CAR_GRIP_LIMIT = "vCar_grip_limit"
    IS_APEX = "isApex"
    TIME = "time"
    V_CAR = "vCar"
    V_CAR_START = "vCar_start"
    V_CAR_END = "vCar_end"
    LONG_ACCEL = "accelLong"
    LAT_ACCEL = "accelLat"
    SOC = "SOC"
    T_CELL = "TCell"
    WEIGHT = "weight"
    F_CENTRIPETAL = "FCentripetal"
    DOWNFORCE = "FDownforce"
    DRAG = "FDrag"
    RESISTIVE_FX = "FxResistive"
    REQUIRED_FY = "FyRequired"
    NORMAL_FORCE = "FzTotal"
    MOTOR_SPEED = "sMotor"
    MOTOR_TORQUE = "TMotor"
    MOTOR_POWER = "PMotor"
    ACCU_CURRENT = "AAccu"
    HEATING_POWER = "PHeating"
    COOLING_POWER = "PCooling"
    NET_THERMAL_POWER = "PThermalNet"
    LONG_LT = "FLongLT"
    LAT_LT = "FLatLT"


def extract_channels(s: Solution) -> dict[ChannelId, Array1D]:
    """Extract channels from a s to save to file."""
    return {
        ChannelId.S_LAP: np.array([node.track_node.position for node in s]),
        ChannelId.LENGTH: np.array([node.length for node in s]),
        ChannelId.CURVATURE: np.array(
            [node.track_node.curvature for node in s]
        ),
        ChannelId.RADIUS: np.array([node.track_node.radius for node in s]),
        ChannelId.ELEVATION: np.array(
            [node.track_node.elevation for node in s]
        ),
        ChannelId.INCLINATION: np.array(
            [node.track_node.inclination for node in s]
        ),
        ChannelId.SECTOR: np.array([node.sector for node in s]),
        ChannelId.N_LAP: np.array([node.lap_number for node in s]),
        ChannelId.TIME: np.array([node.time for node in s]),
        ChannelId.V_CAR_GRIP_LIMIT: np.array(
            [node.maximum_velocity for node in s]
        ),
        ChannelId.IS_APEX: np.array([node.is_apex() for node in s]),
        ChannelId.V_CAR: np.array([node.average_velocity for node in s]),
        ChannelId.V_CAR_START: np.array([node.initial_velocity for node in s]),
        ChannelId.V_CAR_END: np.array([node.final_velocity for node in s]),
        ChannelId.LONG_ACCEL: np.array(
            [node.longitudinal_acceleration for node in s]
        ),
        ChannelId.LAT_ACCEL: np.array(
            [node.lateral_acceleration for node in s]
        ),
        ChannelId.SOC: np.array([node.transient_variables.soc for node in s]),
        ChannelId.T_CELL: np.array(
            [node.transient_variables.cell_temperature for node in s]
        ),
        ChannelId.WEIGHT: np.array(
            [node.get_calculated_vehicle_state().weight for node in s]
        ),
        ChannelId.F_CENTRIPETAL: np.array(
            [
                node.get_calculated_vehicle_state().centripetal_force
                for node in s
            ]
        ),
        ChannelId.DOWNFORCE: np.array(
            [node.get_calculated_vehicle_state().downforce for node in s]
        ),
        ChannelId.DRAG: np.array(
            [node.get_calculated_vehicle_state().drag for node in s]
        ),
        ChannelId.RESISTIVE_FX: np.array(
            [node.get_calculated_vehicle_state().resistive_fx for node in s]
        ),
        ChannelId.REQUIRED_FY: np.array(
            [node.get_calculated_vehicle_state().required_fy for node in s]
        ),
        ChannelId.NORMAL_FORCE: np.array(
            [node.get_calculated_vehicle_state().normal_force for node in s]
        ),
        ChannelId.MOTOR_SPEED: np.array(
            [node.get_calculated_vehicle_state().motor_speed for node in s]
        ),
        ChannelId.MOTOR_TORQUE: np.array(
            [node.get_calculated_vehicle_state().motor_torque for node in s]
        ),
        ChannelId.MOTOR_POWER: np.array(
            [node.get_calculated_vehicle_state().motor_power for node in s]
        ),
        ChannelId.ACCU_CURRENT: np.array(
            [
                node.get_calculated_vehicle_state().accumulator_current
                for node in s
            ]
        ),
        ChannelId.HEATING_POWER: np.array(
            [node.get_calculated_vehicle_state().heating_power for node in s]
        ),
        ChannelId.COOLING_POWER: np.array(
            [node.get_calculated_vehicle_state().cooling_power for node in s]
        ),
        ChannelId.NET_THERMAL_POWER: np.array(
            [
                node.get_calculated_vehicle_state().net_heating_power
                for node in s
            ]
        ),
        ChannelId.LONG_LT: np.array(
            [node.get_calculated_vehicle_state().long_lt for node in s]
        ),
        ChannelId.LAT_LT: np.array(
            [node.get_calculated_vehicle_state().lat_lt for node in s]
        ),
    }


def extract_mesh_channels(mesh: Mesh) -> dict[ChannelId, Array1D]:
    """Extract channels from a mesh to save to file."""
    return {
        ChannelId.S_LAP: np.array([node.position for node in mesh]),
        ChannelId.LENGTH: np.array([node.length for node in mesh]),
        ChannelId.CURVATURE: np.array([node.curvature for node in mesh]),
        ChannelId.ELEVATION: np.array([node.elevation for node in mesh]),
        ChannelId.INCLINATION: np.array([node.inclination for node in mesh]),
        ChannelId.BANKING: np.array([node.banking for node in mesh]),
    }


class SolutionDataFrame:
    """This class stores channels in a dataframe."""

    _df: polars.DataFrame

    def __init__(self, df: polars.DataFrame) -> None:
        self._df = df

    @staticmethod
    def from_dataframe(df: polars.DataFrame) -> SolutionDataFrame:
        return SolutionDataFrame(df)

    @staticmethod
    def from_channels(channels: dict[ChannelId, Array1D]) -> SolutionDataFrame:
        return SolutionDataFrame(polars.DataFrame(channels))

    @staticmethod
    def from_solution(solution: Solution) -> SolutionDataFrame:
        return SolutionDataFrame.from_channels(extract_channels(solution))

    @staticmethod
    def from_mesh(mesh: Mesh) -> SolutionDataFrame:
        return SolutionDataFrame.from_channels(extract_mesh_channels(mesh))

    @property
    def df(self) -> polars.DataFrame:
        return self._df

    @property
    def channel_count(self) -> int:
        return len(self._df.columns)

    @property
    def row_count(self) -> int:
        return len(self._df)

    def get_channel(
        self, channel_id: ChannelId, *, warn_missing: bool = True
    ) -> Array1D:
        """
        Get a channel from the solution.
        Returns an array of NaN if the channel is missing.
        """
        if channel_id not in self._df.columns:
            if warn_missing:
                logger.warning("Channel '%s' not found", channel_id)
            return np.full(self.row_count, np.nan, dtype=np.float64)
        return self._df[channel_id].to_numpy()

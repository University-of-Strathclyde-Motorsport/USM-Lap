"""
This package contains higher-order functions for carrying out analysis.
"""

from .compare import ComparisonResults as ComparisonResults
from .compare import compare_vehicles as compare_vehicles
from .coupling import coupling as coupling
from .sensitivity import points_sensitivity as points_sensitivity
from .sweep import sweep_vehicles as sweep_vehicles
from .sweep_1d import SweepSettings as SweepSettings
from .sweep_1d import sweep_1d as sweep_1d
from .vehicle_generator import VehicleGenerator as VehicleGenerator
from .vehicle_generator import geomspace as geomspace
from .vehicle_generator import linspace as linspace
from .vehicle_generator import step_array as step_array

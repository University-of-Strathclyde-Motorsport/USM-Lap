"""
This subpackage defines telemetry channels, which plot data from a simulation.
"""

from .channel import DataChannel as DataChannel
from .channel import DataChannelValues as DataChannelValues
from .channel import ScalarChannel as ScalarChannel
from .channel import ScalarFunction as ScalarFunction
from .channel import ScalarValue as ScalarValue
from .channel import TelemetryChannel as TelemetryChannel
from .scalar_functions import maximum as maximum
from .scalar_functions import minimum as minimum
from .scalar_functions import total as total

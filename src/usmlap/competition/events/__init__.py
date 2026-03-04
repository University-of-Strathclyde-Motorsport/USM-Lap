"""
Package containing code for simulating different events at Formula Student.
"""

from .acceleration import Acceleration
from .autocross import Autocross
from .endurance import Endurance
from .event import EventInterface
from .skidpad import Skidpad

EVENTS: dict[str, type[EventInterface]] = {
    "acceleration": Acceleration,
    "skidpad": Skidpad,
    "autocross": Autocross,
    "endurance": Endurance,
}

"""
This module plots charts of multiple sweeps in a study.
"""

from typing import Annotated

from pydantic import BeforeValidator, Field, PlainSerializer

from usmlap.core.colour import HexColour
from usmlap.core.library import Serialisable
from usmlap.core.nested_dict import KeyPath, format_keypath, parse_keypath


class StudyLineConfig(Serialisable):
    """Configuration options for a study plot."""

    title: str | None = None
    outing_id: str
    colour: HexColour = HexColour("#003366")
    x_value: Annotated[
        KeyPath,
        BeforeValidator(parse_keypath),
        PlainSerializer(format_keypath),
    ]
    y_value: str
    x_label: str | None = None
    y_label: str | None = None


class StudyWaveform(Serialisable):
    """Configuration options for a study waveform."""

    config: str
    outing_id: str


class StudyPlots(Serialisable):
    """A set of plots to generate for a study."""

    line: list[StudyLineConfig] = Field(default_factory=list)
    waveform: list[StudyWaveform] = Field(default_factory=list)

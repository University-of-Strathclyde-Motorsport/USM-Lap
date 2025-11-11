"""
This module contains code for reading track data from an Excel file.
"""

from __future__ import annotations

import math
import os
from abc import ABC, abstractmethod
from collections.abc import Sequence
from enum import Enum
from pathlib import Path
from typing import Annotated, Self, TypeVar, overload

import filepath
import numpy as np
import pandas
from annotated_types import Unit
from pydantic import BaseModel, ConfigDict, Field
from pydantic.dataclasses import dataclass

from utils.array import cumsum, interp_previous

TRACK_LIBRARY = filepath.LIBRARY_ROOT / "tracks"
AVAILABLE_TRACKS = os.listdir(TRACK_LIBRARY)


class Metadata(BaseModel):
    """
    Metadata for a track.

    Attributes:
        name (str): The name of the track.
        country (str): The country the track is located in.
        city (str): The city the track is located near.
    """

    name: str | None
    country: str | None
    city: str | None

    @property
    def display_name(self) -> str:
        """
        The display name for the track.

        If the track has a name, this is returned.
        Otherwise, "Unnamed Track" is returned.
        """
        return self.name if self.name else "Unnamed Track"

    @property
    def location(self) -> str:
        """
        The location of the track.

        Uses the city and/or country attributes, if present.
        Otherwise, an empty string is returned.
        """
        if self.city and self.country:
            location = f"{self.city}, {self.country}"
        elif self.city:
            location = self.city
        elif self.country:
            location = self.country
        else:
            location = ""
        return location

    def __str__(self) -> str:
        return f"{self.display_name}, {self.location}".strip(", ")


class SectionType(Enum):
    """
    Enum representing the type of section of track.
    """

    STRAIGHT = 0
    LEFT = 1
    RIGHT = -1


@dataclass
class ShapeData(object):
    """
    Data describing the shape of the track.

    Attributes:
        segments (list[Segment]): The segments making up the track.
        total_length (float): The total length of the track.
        corner_radius (float): The radius of the section of the track.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # total_length: Annotated[float, Unit("m")]
    segments: list[Segment]

    @property
    def total_length(self) -> float:
        return sum(segment.length for segment in self.segments)

    @property
    def segment_count(self) -> float:
        return len(self.segments)

    def interpolate_curvature(
        self, position: list[float], closed_track: bool = False
    ) -> list[float]:
        lengths = [s.length for s in self.segments]
        end_positions = cumsum(lengths)
        curvature_position = [
            position - (0.5 * length)
            for position, length in zip(end_positions, lengths)
        ]
        curvature_value = [s.curvature for s in self.segments]
        if closed_track:
            curvature_position.append(end_positions[-1] + (0.5 * lengths[0]))
            curvature_value.append(curvature_value[0])
        return np.interp(position, curvature_position, curvature_value).tolist()


@dataclass
class Segment(object):
    """
    Data describing the shape of a section of track.

    Attributes:
        section_type (SectionType):
            The type of track section (STRAIGHT, LEFT, or RIGHT).
        length (float): The length of the track section.
        corner_radius (float): The radius of the section of the track.
    """

    model_config = ConfigDict(
        use_enum_values=True, arbitrary_types_allowed=True
    )

    section_type: SectionType
    length: Annotated[float, Field(gt=0), Unit("m")]
    corner_radius: Annotated[float, Unit("m")]

    def __post_init__(self) -> None:
        if self.section_type == SectionType.STRAIGHT:
            self.corner_radius = math.inf
        else:
            self.corner_radius = self.corner_radius * self.section_type.value

    @property
    def curvature(self) -> float:
        return 1 / self.corner_radius


T = TypeVar("T")


@dataclass
class PositionData[T](Sequence[T], ABC):
    """
    Abstract base class for data recorded against a series of positions.

    Subclasses must implement the `interpolate` method.

    Attributes:
        position (list[float]): The positions of the data.
        value (list[T]): The values of the data at each position.
    """

    position: list[Annotated[float, Field(ge=0), Unit("m")]]
    value: list[T]

    def __post_init__(self) -> None:
        if len(self.position) != len(self.value):
            raise ValueError("position and value must have the same length")

    def __len__(self) -> int:
        return len(self.value)

    @overload
    def __getitem__(self, key: int) -> T: ...

    @overload
    def __getitem__(self, key: slice) -> Sequence[T]: ...

    def __getitem__(self, key: int | slice) -> Sequence[T] | T:
        if isinstance(key, int):
            return self.value[key]
        else:
            return self.__class__(self.position[key], self.value[key])

    @abstractmethod
    def interpolate(self, position: list[float]) -> list[T]: ...


class LocationData(PositionData[float]):
    """
    Base class for data recorded at a number of locations.
    """

    def interpolate(self, position: list[float]) -> list[float]:
        return np.interp(position, self.position, self.value).tolist()


class StartpointData[T](PositionData[T]):
    """
    Base class for data recorded with a series of startpoints.
    """

    def interpolate(self, position: list[float]) -> list[T]:
        return interp_previous(position, self.position, self.value)


@dataclass
class ElevationData(LocationData):
    """
    Data describing the elevation of the track.
    """

    value: list[Annotated[float, Unit("m")]]


@dataclass
class BankingData(LocationData):
    """
    Data describing the banking angle of the track.
    """

    value: list[
        Annotated[float, Field(ge=-math.pi / 2, le=math.pi / 2), Unit("rad")]
    ]


@dataclass
class GripFactorData(StartpointData[float]):
    """
    Data describing the grip factor of the track.
    """

    value: list[Annotated[float, Field(gt=0)]]


@dataclass
class SectorData(StartpointData[int]):
    """
    Data specifying sectors of the track.

    Sector data has no impact on the simulation,
    and is used purely for visualisation.
    """

    value: list[Annotated[int, Field(gt=0)]]

    def list_sectors(self) -> str:
        return ", ".join(str(value) for value in self.value)


class Event(Enum):
    """
    Enum representing the type of event the track is suitable for.

    If a track is used to simulate an unsuitable event,
    a warning will be issued.
    """

    ACCELERATION = "Acceleration"
    SKIDPAD = "Skidpad"
    AUTOX = "AutoX"


class Configuration(Enum):
    """
    Enum representing the configuration of the track.

    A closed track returns back to its starting position.
    An open track can start and end in different locations.
    """

    CLOSED = "Closed"
    OPEN = "Open"

    def __str__(self) -> str:
        return self.name.lower().capitalize()


class Direction(Enum):
    """
    Enum representing the direction of driving.
    """

    FORWARD = 1
    BACKWARD = -1

    def __str__(self) -> str:
        return self.name.lower().capitalize()


class TrackData(BaseModel):
    """
    Contains information about a racetrack.

    Attributes:
        metadata (Metadata): Metadata for the track, such as name and location.
        shape (ShapeData): Data describing the shape of the track.
        elevation (ElevationData): Data describing the track elevation.
        banking (BankingData): Data describing the track banking.
        grip_factor (GripFactorData): Grip factor data for the track.
        sector (SectorData): Data specifying sectors of the track.
        event (Event): The type of event the track is suitable for.
        configuration (Configuration): The configuration of the track.
        direction (Direction): The direction of driving (default = FORWARD).
        mirror (bool): Whether the track should be mirrored (default = False).
    """

    model_config = ConfigDict()

    metadata: Metadata
    shape: ShapeData
    elevation: ElevationData
    banking: BankingData
    grip_factor: GripFactorData
    sector: SectorData
    event: Event
    configuration: Configuration
    direction: Direction = Direction.FORWARD
    mirror: bool = False

    def __str__(self) -> str:
        return (
            f"{self.metadata}\n\n"
            f"Length: {self.shape.total_length} m\n"
            f"Configuration: {str(self.configuration)}\n"
            f"Direction: {str(self.direction)}\n"
            f"Mirrored: {self.mirror}\n\n"
            f"Shape data: {self.shape.segment_count} segments\n"
            f"Elevation data: {len(self.elevation)} points "
            f"(high: {max(self.elevation)} m, low: {min(self.elevation)} m)\n"
            f"Banking data: {len(self.banking)} points "
            f"(max: {math.degrees(max(self.banking, key=abs))}°)\n"
            f"Grip factor data: {len(self.grip_factor)} points "
            f"(max: {max(self.grip_factor)}, min: {min(self.grip_factor)})\n"
            f"Sector data: {len(self.sector)} sectors "
            f"({self.sector.list_sectors()})\n"
        )

    @classmethod
    def load_track_from_spreadsheet(cls, filepath: Path) -> Self:
        reader = TrackReader(filepath)
        return cls(
            metadata=reader.get_metadata(),
            shape=reader.get_shape_data(),
            elevation=reader.get_elevation_data(),
            banking=reader.get_banking_data(),
            grip_factor=reader.get_grip_factor_data(),
            sector=reader.get_sector_data(),
            event=Event.AUTOX,
            configuration=reader.get_configuration(),
            direction=reader.get_direction(),
            mirror=reader.get_mirror(),
        )


def load_track_from_spreadsheet(filename: str) -> TrackData:
    """
    Load a track from the library.

    Args:
        filename (str): The name of the track file.

    Returns:
        track_data (TrackData): The loaded track data.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    try:
        filepath = TRACK_LIBRARY / filename
        reader = TrackReader(filepath)
        return TrackData(
            metadata=reader.get_metadata(),
            shape=reader.get_shape_data(),
            elevation=reader.get_elevation_data(),
            banking=reader.get_banking_data(),
            grip_factor=reader.get_grip_factor_data(),
            sector=reader.get_sector_data(),
            event=Event.AUTOX,
            configuration=reader.get_configuration(),
            direction=reader.get_direction(),
            mirror=reader.get_mirror(),
        )
    except FileNotFoundError:
        error_message = (
            f"Unable to find '{filename}' in track library. "
            f"Available tracks: {AVAILABLE_TRACKS}"
        )
        raise FileNotFoundError(error_message)


class TrackReader(object):
    """
    Reads track data from an OpenLAP Excel spreadsheet.

    Attributes:
        workbook (pandas.ExcelFile): The Excel file containing the track data.
    """

    def __init__(self, filepath: Path) -> None:
        """
        Initialises the TrackReader from a filepath.

        Args:
            filepath (Path): Path to the Excel file to be read.
        """
        self.workbook = pandas.ExcelFile(filepath, engine="openpyxl")

    def _get_info(self) -> pandas.DataFrame:
        return pandas.read_excel(
            self.workbook,
            header=None,
            sheet_name="Info",
            usecols="A:B",
            index_col=0,
            dtype=str,
        )

    def get_metadata(self) -> Metadata:
        """Returns the metadata for the track."""
        info = self._get_info()
        return Metadata(
            name=str(info.at["Name", 1]),
            country=str(info.at["Country", 1]),
            city=str(info.at["City", 1]),
        )

    def get_shape_data(self) -> ShapeData:
        """Returns the shape data for the track."""
        dataframe = pandas.read_excel(self.workbook, sheet_name="Shape")
        segments = [
            Segment(
                section_type=SectionType[row["Type"].upper()],
                length=row["Section Length"],
                corner_radius=row["Corner Radius"],
            )
            for _, row in dataframe.iterrows()
        ]
        return ShapeData(segments=segments)

    def get_elevation_data(self) -> ElevationData:
        """Returns the elevation data for the track."""
        dataframe = pandas.read_excel(self.workbook, sheet_name="Elevation")
        return ElevationData(
            position=dataframe["Point [m]"].tolist(),
            value=dataframe["Elevation [m]"].tolist(),
        )

    def get_banking_data(self) -> BankingData:
        """Returns the banking data for the track."""
        dataframe = pandas.read_excel(self.workbook, sheet_name="Banking")
        return BankingData(
            position=dataframe["Point [m]"].tolist(),
            value=dataframe["Banking [deg]"].apply(math.radians).tolist(),
        )

    def get_grip_factor_data(self) -> GripFactorData:
        """Returns the grip factor data for the track."""
        dataframe = pandas.read_excel(self.workbook, sheet_name="Grip Factors")
        return GripFactorData(
            position=dataframe["Start Point [m]"].tolist(),
            value=dataframe["Grip Factor [-]"].tolist(),
        )

    def get_sector_data(self) -> SectorData:
        """Returns the sector data for the track."""
        dataframe = pandas.read_excel(self.workbook, sheet_name="Sectors")
        return SectorData(
            position=dataframe["Start Point [m]"].tolist(),
            value=dataframe["Sector"].tolist(),
        )

    def get_configuration(self) -> Configuration:
        """Returns the configuration of the track."""
        return Configuration[
            str(self._get_info().at["Configuration", 1]).upper()
        ]

    def get_direction(self) -> Direction:
        """Returns the direction of driving."""
        return Direction[str(self._get_info().at["Direction", 1]).upper()]

    def get_mirror(self) -> bool:
        """Returns whether the track should be mirrored."""
        mirror_str = str(self._get_info().at["Mirror", 1])
        return True if mirror_str.lower() in ["on", "yes", "true"] else False

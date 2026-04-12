"""
This module contains code for reading track data from an Excel file.
"""

from __future__ import annotations

import math
import os
from enum import Enum, IntEnum
from pathlib import Path
from typing import Optional, Self

import pandas
from pydantic import BaseModel, Field

from usmlap import filepath

TRACK_LIBRARY = filepath.LIBRARY_ROOT / "tracks"
AVAILABLE_TRACKS = os.listdir(TRACK_LIBRARY)


UNKNOWN_LOCATION = "Unknown"


class SectionType(IntEnum):
    """
    Enum representing the type of section of track.
    """

    STRAIGHT = 0
    LEFT = 1
    RIGHT = -1


class ShapeData(BaseModel):
    """
    Data describing the shape of the track.

    Attributes:
        length (float): The length of the track section.
        curvature (float): The curvature of the track section.
            Positive for left, negative for right.
    """

    length: float = Field(gt=0)
    curvature: float


class SectorData(BaseModel):
    """
    Data describing sectors of the track.

    Attributes:
        start_position (float): The start position of the sector.
        label (str): An optional label for the sector (default = "").
            If left blank, labels will be automatically generated.
        timed (bool): Whether the sector should be timed (default = True).
    """

    start_position: float = Field(ge=0)
    label: str = ""
    timed: bool = True

    @classmethod
    def default(cls) -> str:
        return "Sector 1"


class ElevationData(BaseModel):
    """
    Data describing the elevation of the track.

    Attributes:
        position (float): The position that the data was recorded.
        elevation (float): The elevation of the track at the position.
    """

    position: float = Field(ge=0)
    elevation: float

    @classmethod
    def default(cls) -> float:
        return 0


class BankingData(BaseModel):
    """
    Data describing the banking angle of the track.

    Attributes:
        position (float): The position that the data was recorded.
        angle (float): The banking angle of the track at the position.
        TODO: Sign convention?
    """

    position: float = Field(ge=0)
    angle: float = Field(ge=-math.pi / 2, le=math.pi / 2)

    @classmethod
    def default(cls) -> float:
        return 0


class GripFactorData(BaseModel):
    """
    Data describing the grip factor of the track.

    Attributes:
        position (float): The position that the data was recorded.
        grip_factor (float): The grip factor of the track at the position.
    """

    position: float = Field(ge=0)
    grip_factor: float = Field(gt=0)

    @classmethod
    def default(cls) -> float:
        return 1


class Event(Enum):
    """
    Enum representing the type of event the track is suitable for.

    If a track is used to simulate an unsuitable event,
    a warning will be issued.
    """

    ACCELERATION = "acceleration"
    SKIDPAD = "skidpad"
    AUTOX = "autocross"


class Configuration(Enum):
    """
    Enum representing the configuration of the track.

    A closed track returns back to its starting position.
    An open track can start and end in different locations.
    """

    CLOSED = "closed"
    OPEN = "open"

    def __str__(self) -> str:
        return self.name.lower()


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
        print_name (str): The name of the track.
        country (str): The country the track is located in.
        city (str): The city the track is located near.
        shape (list[ShapeData]): Data describing the shape of the track.
        elevation (list[ElevationData]): Data describing the track elevation.
        banking (list[BankingData]): Data describing the track banking.
        grip_factor (list[GripFactorData]): Grip factor data for the track.
        sector (list[SectorData]): Data specifying sectors of the track.
        event (Optional[Event]): The type of event the track is suitable for.
            A warning will be issued if the track is used
            to simulate an unsuitable event.
        configuration (Configuration): The configuration of the track.
        # direction (Direction): The direction of driving (default = FORWARD).
        # mirror (bool): Whether the track should be mirrored (default = False).
    """

    print_name: str
    country: Optional[str] = None
    city: Optional[str] = None
    configuration: Configuration
    event: Optional[Event] = None
    shape: list[ShapeData]
    elevation: list[ElevationData] = Field(default_factory=list)
    banking: list[BankingData] = Field(default_factory=list)
    grip_factor: list[GripFactorData] = Field(default_factory=list)
    sectors: list[SectorData] = Field(default_factory=list)
    # direction: Direction = Direction.FORWARD
    # mirror: bool = False

    def __post_init__(self) -> None:
        self.generate_sector_labels()

    def __str__(self) -> str:
        return (
            f"Name: {self.print_name}\n"
            f"Location: {self.location}\n\n"
            f"Total length: {self.total_length} m\n"
            f"Configuration: {str(self.configuration)}\n"
            # f"Direction: {str(self.direction)}\n"
            # f"Mirrored: {self.mirror}\n\n"
            f"Shape data: {len(self.shape)} segments\n"
            f"Elevation: "
            f"high = {self.max_elevation} m, low = {self.min_elevation} m\n"
            f"Banking: "
            f"max = {self.max_banking_angle}°\n"
            f"Grip factor: "
            f"max = {self.max_grip_factor}, min = {self.min_grip_factor}\n"
            f"Sectors: {len(self.sectors)} "
            f"({', '.join(sector.label for sector in self.sectors)})\n"
        )

    @property
    def total_length(self) -> float:
        return sum(segment.length for segment in self.shape)

    @property
    def max_elevation(self) -> float:
        if self.elevation:
            return max(data.elevation for data in self.elevation)
        else:
            return ElevationData.default()

    @property
    def min_elevation(self) -> float:
        if self.elevation:
            return min(data.elevation for data in self.elevation)
        else:
            return ElevationData.default()

    @property
    def max_banking_angle(self) -> float:
        if self.banking:
            return math.degrees(max([abs(data.angle) for data in self.banking]))
        else:
            return BankingData.default()

    @property
    def max_grip_factor(self) -> float:
        if self.grip_factor:
            return max(data.grip_factor for data in self.grip_factor)
        else:
            return GripFactorData.default()

    @property
    def min_grip_factor(self) -> float:
        if self.grip_factor:
            return min(data.grip_factor for data in self.grip_factor)
        else:
            return GripFactorData.default()

    @property
    def location(self) -> str:
        """
        The location of the track.

        Uses the city and/or country attributes, if present.
        Otherwise, "Unknown" is returned.
        """
        if self.city and self.country:
            location = f"{self.city}, {self.country}"
        elif self.city:
            location = self.city
        elif self.country:
            location = self.country
        else:
            location = UNKNOWN_LOCATION
        return location

    def generate_sector_labels(self) -> None:
        for i, sector in enumerate(self.sectors):
            if sector.label is None:
                sector.label = f"Sector {i + 1}"

    def list_sector_labels(self) -> list[str]:
        return [sector.label for sector in self.sectors]

    @classmethod
    def from_json(cls, filename: str) -> Self:
        """
        Load a track from a JSON file in the library.

        Args:
            filename (str): The name of the track file.

        Returns:
            track_data (TrackData): The loaded track data.

        Raises:
            FileNotFoundError: If the file does not exist.

        """
        try:
            filepath = TRACK_LIBRARY / filename
            with open(filepath, "r") as file:
                data = file.read()

        except FileNotFoundError:
            error_message = (
                f"Unable to find '{filename}' in track library. "
                f" Available tracks: {AVAILABLE_TRACKS}"
            )
            raise FileNotFoundError(error_message)

        return cls.model_validate_json(data)

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)


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
        filepath = TRACK_LIBRARY / "legacy" / filename
        reader = TrackReader(filepath)
        return TrackData(
            print_name=reader.get_print_name(),
            country=reader.get_country(),
            city=reader.get_city(),
            shape=reader.get_shape_data(),
            elevation=reader.get_elevation_data(),
            banking=reader.get_banking_data(),
            grip_factor=reader.get_grip_factor_data(),
            sectors=reader.get_sector_data(),
            event=Event.AUTOX,
            configuration=reader.get_configuration(),
            # direction=reader.get_direction(),
            # mirror=reader.get_mirror(),
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

    def get_print_name(self) -> str:
        return str(self._get_info().at["Name", 1])

    def get_country(self) -> str:
        return str(self._get_info().at["Country", 1])

    def get_city(self) -> str:
        return str(self._get_info().at["City", 1])

    def get_shape_data(self) -> list[ShapeData]:
        """Returns the shape data for the track."""

        def get_curvature(section_type: SectionType, radius: float) -> float:
            """Calculate curvature from section type and corner radius."""
            if section_type == SectionType.STRAIGHT:
                return 0
            elif section_type == SectionType.LEFT:
                return 1 / radius
            elif section_type == SectionType.RIGHT:
                return -1 / radius
            else:
                raise ValueError(f"Invalid section type: {section_type}")

        dataframe = pandas.read_excel(self.workbook, sheet_name="Shape")
        shape_data = [
            ShapeData(
                length=row["Section Length"],
                curvature=get_curvature(
                    section_type=SectionType[row["Type"].upper()],
                    radius=row["Corner Radius"],
                ),
            )
            for _, row in dataframe.iterrows()
        ]
        return shape_data

    def get_elevation_data(self) -> list[ElevationData]:
        """Returns the elevation data for the track."""
        dataframe = pandas.read_excel(self.workbook, sheet_name="Elevation")
        elevation_data = [
            ElevationData(
                position=row["Point [m]"], elevation=row["Elevation [m]"]
            )
            for _, row in dataframe.iterrows()
        ]
        return elevation_data

    def get_banking_data(self) -> list[BankingData]:
        """Returns the banking data for the track."""
        dataframe = pandas.read_excel(self.workbook, sheet_name="Banking")
        banking_data = [
            BankingData(
                position=row["Point [m]"],
                angle=math.radians(row["Banking [deg]"]),
            )
            for _, row in dataframe.iterrows()
        ]
        return banking_data

    def get_grip_factor_data(self) -> list[GripFactorData]:
        """Returns the grip factor data for the track."""
        dataframe = pandas.read_excel(self.workbook, sheet_name="Grip Factors")
        grip_factor_data = [
            GripFactorData(
                position=row["Start Point [m]"],
                grip_factor=row["Grip Factor [-]"],
            )
            for _, row in dataframe.iterrows()
        ]
        return grip_factor_data

    def get_sector_data(self) -> list[SectorData]:
        """Returns the sector data for the track."""
        dataframe = pandas.read_excel(self.workbook, sheet_name="Sectors")
        sector_data = [
            SectorData(
                start_position=row["Start Point [m]"], label=str(row["Sector"])
            )
            for _, row in dataframe.iterrows()
        ]
        return sector_data

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


def save_track_data(
    track_data: TrackData, filename: Optional[str] = None
) -> None:
    """Save track data to a JSON file."""
    if filename is None:
        filename = track_data.print_name

    filepath = TRACK_LIBRARY / f"{filename}.json"
    if filepath.exists():
        error_message = f"Error saving track; file '{filename}' already exists."
        raise FileExistsError(error_message)

    with open(filepath, "w") as f:
        f.write(track_data.to_json())


# class Metadata(BaseModel):
#     """
#     Metadata for a track.

#     Attributes:
#         name (str): The name of the track.
#         country (str): The country the track is located in.
#         city (str): The city the track is located near.
#     """

#     name: str
#     country: Optional[str] = None
#     city: Optional[str] = None

#     @property
#     def display_name(self) -> str:
#         """
#         The display name for the track.

#         If the track has a name, this is returned.
#         Otherwise, "Unnamed Track" is returned.
#         """
#         return self.name if self.name else "Unnamed Track"

#     @property
#     def location(self) -> str:
#         """
#         The location of the track.

#         Uses the city and/or country attributes, if present.
#         Otherwise, an empty string is returned.
#         """
#         if self.city and self.country:
#             location = f"{self.city}, {self.country}"
#         elif self.city:
#             location = self.city
#         elif self.country:
#             location = self.country
#         else:
#             location = ""
#         return location

#     def __str__(self) -> str:
#         return f"{self.display_name}, {self.location}".strip(", ")


# @dataclass
# class ShapeData(object):
#     """
#     Data describing the shape of the track.

#     Attributes:
#         segments (list[Segment]): The segments making up the track.
#         total_length (float): The total length of the track.
#         corner_radius (float): The radius of the section of the track.
#     """

#     model_config = ConfigDict(arbitrary_types_allowed=True)

#     # total_length: Annotated[float, Unit("m")]
#     segments: list[Segment]

#     @property
#     def total_length(self) -> float:
#         return sum(segment.length for segment in self.segments)

#     @property
#     def segment_count(self) -> float:
#         return len(self.segments)

#     def interpolate_curvature(
#         self, position: list[float], closed_track: bool = False
#     ) -> list[float]:
#         lengths = [s.length for s in self.segments]
#         end_positions = cumsum(lengths)
#         curvature_position = [
#             position - (0.5 * length)
#             for position, length in zip(end_positions, lengths)
#         ]
#         curvature_value = [s.curvature for s in self.segments]
#         if closed_track:
#             curvature_position.append(end_positions[-1] + (0.5 * lengths[0]))
#             curvature_value.append(curvature_value[0])
#         return np.interp(position, curvature_position, curvature_value).tolist()


# @dataclass
# class Segment(object):
#     """
#     Data describing the shape of a section of track.

#     Attributes:
#         section_type (SectionType):
#             The type of track section (STRAIGHT, LEFT, or RIGHT).
#         length (float): The length of the track section.
#         corner_radius (float): The radius of the section of the track.
#     """

#     model_config = ConfigDict(
#         use_enum_values=True, arbitrary_types_allowed=True
#     )

#     section_type: SectionType
#     length: Annotated[float, Field(gt=0), Unit("m")]
#     corner_radius: Annotated[float, Unit("m")]

#     def __post_init__(self) -> None:
#         if self.section_type == SectionType.STRAIGHT:
#             self.corner_radius = math.inf
#         else:
#             self.corner_radius = self.corner_radius * self.section_type.value

#     @property
#     def curvature(self) -> float:
#         return 1 / self.corner_radius


# @dataclass
# class PositionData[T](Sequence[T], ABC):
#     """
#     Abstract base class for data recorded against a series of positions.

#     Subclasses must implement the `interpolate` method.

#     Attributes:
#         position (list[float]): The positions of the data.
#         value (list[T]): The values of the data at each position.
#     """

#     position: list[Annotated[float, Field(ge=0), Unit("m")]]
#     value: list[T]

#     def __post_init__(self) -> None:
#         if len(self.position) != len(self.value):
#             raise ValueError("position and value must have the same length")

#     def __len__(self) -> int:
#         return len(self.value)

#     @overload
#     def __getitem__(self, key: int) -> T: ...

#     @overload
#     def __getitem__(self, key: slice) -> Sequence[T]: ...

#     def __getitem__(self, key: int | slice) -> Sequence[T] | T:
#         if isinstance(key, int):
#             return self.value[key]
#         else:
#             return self.__class__(self.position[key], self.value[key])

#     @abstractmethod
#     def interpolate(self, position: list[float]) -> list[T]: ...


# class LocationData(PositionData[float]):
#     """
#     Base class for data recorded at a number of locations.
#     """

#     def interpolate(self, position: list[float]) -> list[float]:
#         return np.interp(position, self.position, self.value).tolist()


# class StartpointData[T](PositionData[T]):
#     """
#     Base class for data recorded with a series of startpoints.
#     """

#     def interpolate(self, position: list[float]) -> list[T]:
#         return interp_previous(position, self.position, self.value)


# @dataclass
# class ElevationData(LocationData):
#     """
#     Data describing the elevation of the track.
#     """

#     value: list[Annotated[float, Unit("m")]]


# @dataclass
# class BankingData(LocationData):
#     """
#     Data describing the banking angle of the track.
#     """

#     value: list[
#         Annotated[float, Field(ge=-math.pi / 2, le=math.pi / 2), Unit("rad")]
#     ]


# @dataclass
# class GripFactorData(StartpointData[float]):
#     """
#     Data describing the grip factor of the track.
#     """

#     value: list[Annotated[float, Field(gt=0)]]


# @dataclass
# class SectorData(StartpointData[int]):
#     """
#     Data specifying sectors of the track.

#     Sector data has no impact on the simulation,
#     and is used purely for visualisation.
#     """

#     value: list[Annotated[int, Field(gt=0)]]

#     def list_sectors(self) -> str:
#         return ", ".join(str(value) for value in self.value)

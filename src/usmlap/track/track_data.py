"""
This module contains code for reading track data from an Excel file.
"""

from enum import Enum
from typing import Annotated, Self
from annotated_types import Unit
from pydantic import BaseModel, Field, ConfigDict
from abc import ABC
from math import pi, inf
import pandas

from utils.conversion import degrees_to_radians, radians_to_degrees


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


class ShapeData(BaseModel):
    """
    Data describing the shape of a section of track.

    Attributes:
        section_type (SectionType):
            The type of track section (STRAIGHT, LEFT, or RIGHT).
        length (float): The length of the track section.
        corner_radius (float): The radius of the section of the track.
    """

    model_config = ConfigDict(use_enum_values=True)

    section_type: SectionType
    length: Annotated[float, Field(gt=0), Unit("m")]
    corner_radius: Annotated[float, Unit("m")]

    def __init__(
        self, section_type: SectionType, length: float, corner_radius: float
    ) -> None:
        if section_type == SectionType.STRAIGHT:
            corner_radius = inf
        else:
            corner_radius = corner_radius * section_type.value
        super().__init__(
            section_type=section_type,
            length=length,
            corner_radius=corner_radius,
        )

    @property
    def curvature(self) -> float:
        return 1 / self.corner_radius


class LocationData(ABC, BaseModel):
    """
    Abstract base class for data recorded over a number of locations.
    """

    location: Annotated[float, Field(ge=0), Unit("m")]


# class LocationData2(ABC, BaseModel):
#     """
#     Abstract base class for data recorded over a number of locations.
#     """

#     location: list[Annotated[float, Field(ge=0), Unit("m")]]
#     value: list[float]

#     def __init__(self, location: list[float], value: list[float]) -> None:
#         assert len(location) == len(value), (
#             "location and value must have the same length"
#         )
#         super().__init__(location=location, value=value)

#     def length(self) -> float:
#         return len(self.location)

#     def __iter__(self):
#         yield from zip(self.location, self.value)

#     def max(self) -> float:
#         return max(self.value)

#     def min(self) -> float:
#         return min(self.value)


class ElevationData(LocationData):
    """
    Data describing the elevation of the track.
    """

    elevation: Annotated[float, Unit("m")]


# class ElevationData2(LocationData2):
#     """
#     Data describing the elevation of the track.
#     """

#     value: list[Annotated[float, Unit("m")]]


class BankingData(LocationData):
    """
    Data describing the banking angle of the track.
    """

    banking: Annotated[float, Field(ge=-pi / 2, le=pi / 2), Unit("rad")]


class GripFactorData(BaseModel):
    """
    Data describing the grip factor of the track.
    """

    startpoint: Annotated[float, Field(ge=0), Unit("m")]
    grip_factor: Annotated[float, Field(gt=0)]


class SectorData(BaseModel):
    """
    Data specifying sectors of the track.

    Sector data has no impact on the simulation,
    and is used purely for visualisation.
    """

    startpoint: Annotated[float, Field(ge=0), Unit("m")]
    sector_number: Annotated[int, Field(gt=0)]


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
        shape (list[ShapeData]): Data describing the shape of the track.
        elevation (list[ElevationData]): Data describing the track elevation.
        banking (list[BankingData]): Data describing the track banking.
        grip_factor (list[GripFactorData]): Grip factor data for the track.
        sector (list[SectorData]): Data specifying sectors of the track.
        event (Event): The type of event the track is suitable for.
        configuration (Configuration): The configuration of the track.
        direction (Direction): The direction of driving (default = FORWARD).
        mirror (bool): Whether the track should be mirrored (default = False).
    """

    model_config = ConfigDict()

    metadata: Metadata
    shape: list[ShapeData]
    elevation: list[ElevationData]
    banking: list[BankingData]
    grip_factor: list[GripFactorData]
    sector: list[SectorData]
    event: Event
    configuration: Configuration
    direction: Direction = Direction.FORWARD
    mirror: bool = False

    @property
    def total_length(self) -> float:
        return sum(segment.length for segment in self.shape)

    @property
    def max_elevation(self) -> float:
        return max(point.elevation for point in self.elevation)

    @property
    def min_elevation(self) -> float:
        return min(point.elevation for point in self.elevation)

    @property
    def max_banking(self) -> float:
        return max(abs(point.banking) for point in self.banking)

    @property
    def max_grip_factor(self) -> float:
        return max(point.grip_factor for point in self.grip_factor)

    @property
    def min_grip_factor(self) -> float:
        return min(point.grip_factor for point in self.grip_factor)

    def list_sectors(self) -> str:
        return ", ".join(str(sector.sector_number) for sector in self.sector)

    def __str__(self) -> str:
        return (
            f"{self.metadata}\n\n"
            f"Length: {self.total_length} m\n"
            f"Configuration: {str(self.configuration)}\n"
            f"Direction: {str(self.direction)}\n"
            f"Mirrored: {self.mirror}\n\n"
            f"Shape data: {len(self.shape)} segments\n"
            f"Elevation data: {len(self.elevation)} points "
            f"(high: {self.max_elevation} m, low: {self.min_elevation} m)\n"
            f"Banking data: {len(self.banking)} points "
            f"(max: {radians_to_degrees(self.max_banking)}°)\n"
            f"Grip factor data: {len(self.grip_factor)} points "
            f"(max: {self.max_grip_factor}, min: {self.min_grip_factor})\n"
            f"Sector data: {len(self.sector)} sectors ({self.list_sectors()})\n"
        )

    @classmethod
    def load_track_from_spreadsheet(cls, filepath: str) -> Self:
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


class TrackReader(object):
    """
    Reads track data from an OpenLAP Excel spreadsheet.

    Attributes:
        workbook (pandas.ExcelFile): The Excel file containing the track data.
    """

    def __init__(self, filepath: str) -> None:
        """
        Initialises the TrackReader from a filepath.

        Args:
            filepath (str): Path to the Excel file to be read.
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

    def get_shape_data(self) -> list[ShapeData]:
        """Returns the shape data for the track."""
        dataframe = pandas.read_excel(self.workbook, sheet_name="Shape")
        return [
            ShapeData(
                section_type=SectionType[row["Type"].upper()],
                length=row["Section Length"],
                corner_radius=row["Corner Radius"],
            )
            for _, row in dataframe.iterrows()
        ]

    def get_elevation_data(self) -> list[ElevationData]:
        """Returns the elevation data for the track."""
        dataframe = pandas.read_excel(self.workbook, sheet_name="Elevation")
        # return ElevationData2(
        #     location=dataframe["Point [m]"].tolist(),
        #     value=dataframe["Elevation [m]"].tolist(),
        # )
        return [
            ElevationData(
                location=row["Point [m]"], elevation=row["Elevation [m]"]
            )
            for _, row in dataframe.iterrows()
        ]

    def get_banking_data(self) -> list[BankingData]:
        """Returns the banking data for the track."""
        dataframe = pandas.read_excel(self.workbook, sheet_name="Banking")
        return [
            BankingData(
                location=row["Point [m]"],
                banking=degrees_to_radians(row["Banking [deg]"]),
            )
            for _, row in dataframe.iterrows()
        ]

    def get_grip_factor_data(self) -> list[GripFactorData]:
        """Returns the grip factor data for the track."""
        dataframe = pandas.read_excel(self.workbook, sheet_name="Grip Factors")
        return [
            GripFactorData(
                startpoint=row["Start Point [m]"],
                grip_factor=row["Grip Factor [-]"],
            )
            for _, row in dataframe.iterrows()
        ]

    def get_sector_data(self) -> list[SectorData]:
        """Returns the sector data for the track."""
        dataframe = pandas.read_excel(self.workbook, sheet_name="Sectors")
        return [
            SectorData(
                startpoint=row["Start Point [m]"],
                sector_number=row["Sector"],
            )
            for _, row in dataframe.iterrows()
        ]

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

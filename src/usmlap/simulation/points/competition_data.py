"""
This module contains code for handling competition data.
"""

from pydantic import BaseModel
from typing import Any, Self
import json


class CompetitionData(BaseModel):
    """
    Scores from Formula Student competition,
    used to calculate points scored at competition.

    Attributes:
        acceleration_t_min (float): The minimum time for the acceleration event.
        skidpad_t_min (float): The minimum time for the skidpad event.
        autocross_t_min (float): The minimum time for the autocross event.
        endurance_t_min (float): The minimum time for the endurance event.
    """

    dataset: str
    acceleration_t_min: float
    skidpad_t_min: float
    autocross_t_min: float
    endurance_t_min: float

    @staticmethod
    def _get_library_path() -> str:
        return "appdata/library/competition/points.json"

    @classmethod
    def load_library(cls) -> dict[str, dict[str, Any]]:
        with open(cls._get_library_path(), "r") as library_file:
            return json.load(library_file)

    @classmethod
    def list_datasets(cls) -> list[str]:
        return list(cls.load_library().keys())

    @classmethod
    def check_dataset_exists(cls, name: str) -> None:
        available_datasets = cls.list_datasets()
        if name not in available_datasets:
            error_message = (
                f"Competition dataset '{name}' not found "
                f"(available datasets: {available_datasets})"
            )
            raise KeyError(error_message)

    @classmethod
    def get_dataset(cls, name: str) -> Self:
        cls.check_dataset_exists(name)
        library = cls.load_library()
        dataset = library[name]
        dataset["dataset"] = name
        return cls.model_validate(dataset)

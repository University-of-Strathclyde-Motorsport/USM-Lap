"""
This module provides methods for reading and writing Pydantic models.
"""

import logging
from pathlib import Path

import yaml
from pydantic import BaseModel

logger = logging.getLogger(__name__)

JSON_INDENT = 2


def save_object_to_json(
    obj: BaseModel, filepath: Path, *, overwrite: bool = False
) -> None:
    """Save a Pydantic object to JSON."""
    obj_name = obj.__class__.__name__
    if filepath.exists() and not overwrite:
        logger.warning(
            "Unable to save %s to '%s'; file already exists",
            obj_name,
            filepath,
        )
        return

    filepath.parent.mkdir(exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as file:
        json = obj.model_dump_json(indent=JSON_INDENT)
        file.write(json)

    logger.info("Saved %s to '%s'", obj_name, filepath)


def read_object_from_yaml[T: BaseModel](type_: type[T], filepath: Path) -> T:
    """Read a Pydantic object from a .yaml file."""
    with open(filepath, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return type_.model_validate(data)

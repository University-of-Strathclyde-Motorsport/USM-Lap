from typing import Annotated, TypeVar
from pydantic import Field

T = TypeVar("T")


class FrontRear(tuple[T, T]):
    @property
    def front(self) -> T:
        return self[0]

    @property
    def rear(self) -> T:
        return self[1]

    def __str__(self) -> str:
        return f"front: {self.front}, rear: {self.rear}"


type Percentage = Annotated[float, Field(ge=0, le=1)]

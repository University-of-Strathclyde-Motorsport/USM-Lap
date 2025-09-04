from typing import Generic, TypeVar

T = TypeVar("T")


class FrontRear(Generic[T]):
    def __init__(self, front: T, rear: T):
        self.front = front
        self.rear = rear

    def __str__(self) -> str:
        return f"front: {self.front}, rear: {self.rear}"

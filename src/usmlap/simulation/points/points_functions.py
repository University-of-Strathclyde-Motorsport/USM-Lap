"""
This module contains functions for calculating points scored at competition.
"""

from abc import ABC, abstractmethod


class PointsFunctions(ABC):
    """
    Functions for calculating points scored at Formula Student competitions.
    """

    @staticmethod
    @abstractmethod
    def calculate_acceleration_points(t_team: float, t_min: float) -> float:
        """
        Calculate the points scored in the acceleration event.

        Args:
            t_team (float): The acceleration time set by the car.
            t_min (float): The acceleration time of the fastest team.

        Returns:
            score (float): The points scored in the acceleration event.
        """
        ...

    @staticmethod
    @abstractmethod
    def calculate_skidpad_points(t_team: float, t_min: float) -> float:
        """
        Calculate the points scored in the skidpad event.

        Args:
            t_team (float): The skidpad time set by the car.
            t_min (float): The skidpad time of the fastest team.

        Returns:
            score (float): The points scored in the skidpad event.
        """
        ...

    @staticmethod
    @abstractmethod
    def calculate_autocross_points(t_team: float, t_min: float) -> float:
        """
        Calculate the points scored in the autocross event.

        Args:
            t_team (float): The autocross time set by the car.
            t_min (float): The autocross time of the fastest team.

        Returns:
            score (float): The points scored in the autocross event.
        """
        ...

    @staticmethod
    @abstractmethod
    def calculate_endurance_points(t_team: float, t_min: float) -> float:
        """
        Calculate the points scored in the endurance event.

        Args:
            t_team (float): The endurance time set by the car.
            t_min (float): The endurance time of the fastest team.

        Returns:
            score (float): The points scored in the endurance event.
        """
        ...


class FSUKPointsFunctions(PointsFunctions):
    """
    Points functions for Formula Student UK.
    """

    @staticmethod
    def calculate_acceleration_points(t_team: float, t_min: float) -> float:
        t_min = min(t_team, t_min)
        t_max = t_min * 1.5
        score = 65 * ((t_max / t_team) - 1) / ((t_max / t_min) - 1)
        base_points = 5
        return base_points + score

    @staticmethod
    def calculate_skidpad_points(t_team: float, t_min: float) -> float:
        t_min = min(t_team, t_min)
        t_max = t_min * 1.25
        score = 70 * ((t_max / t_team) ** 2 - 1) / ((t_max / t_min) ** 2 - 1)
        base_points = 5
        return base_points + score

    @staticmethod
    def calculate_autocross_points(t_team: float, t_min: float) -> float:
        t_min = min(t_team, t_min)
        t_max = t_min * 1.45
        score = 95 * ((t_max / t_team) - 1) / ((t_max / t_min) - 1)
        base_points = 5
        return base_points + score

    @staticmethod
    def calculate_endurance_points(t_team: float, t_min: float) -> float:
        t_min = min(t_team, t_min)
        t_max = t_min * 1.45
        score = 225 * ((t_max / t_team) - 1) / ((t_max / t_min) - 1)
        base_points = 25
        return base_points + score

"""
This module contains code for calculating points from competition results.
"""

from dataclasses import dataclass

from usmlap.vehicle.common import Component

type CompetitionPoints = dict[str, float]


class CompetitionData(Component, library="competition"):
    """
    Data from a Formula Student competition.
    """

    print_name: str
    acceleration_t_min: float
    skidpad_t_min: float
    autocross_t_min: float
    endurance_t_min: float
    efficiency_ef_min: float


@dataclass
class PointsCoefficients(object):
    """
    Coefficients for points formula.

    Attributes:
        label (str): Label for the event.
        p_max (float): The maximum points available for the event.
        p_min (float): The minimum points awarded for completing the event.
        x_max_scalar (float): Multiplied by `x_min` to determine `x_max`.
            If `x_team` >= `x_max`, only the minimum points are awarded.
    """

    label: str
    p_max: float
    p_min: float
    x_max_scalar: float


def calculate_points(
    x_team: float, x_min: float, coefficients: PointsCoefficients
) -> tuple[str, float]:
    """
    Calculate points scored in a competition event.

    Args:
        x_team (float): The time or efficiency factor of the car.
        x_min (float): The best time or efficiency factor of any other team.
        coefficients (PointsCoefficients): Points coefficients for the event.

    Returns:
        label (str): Label for the event.
        points (float): Competition points scored in the event.
    """

    p_max = coefficients.p_max
    p_min = coefficients.p_min
    x_min = min(x_team, x_min)
    x_max = coefficients.x_max_scalar * x_min

    if x_team >= x_max:
        points = p_min
    else:
        scalar = ((x_max - x_team) / (x_max - x_min)) ** 2
        points = p_min + (p_max - p_min) * scalar

    return coefficients.label, points


ACCELERATION_COEFFICIENTS = PointsCoefficients(
    "acceleration", p_max=75, p_min=3.5, x_max_scalar=1.7
)

SKIDPAD_COEFFICIENTS = PointsCoefficients(
    "skidpad", p_max=75, p_min=3.5, x_max_scalar=1.35
)

AUTOCROSS_COEFFICIENTS = PointsCoefficients(
    "autocross", p_max=100, p_min=5, x_max_scalar=1.4
)

ENDURANCE_COEFFICIENTS = PointsCoefficients(
    "endurance", p_max=325, p_min=25, x_max_scalar=1.5
)

EFFICIENCY_COEFFICIENTS = PointsCoefficients(
    "efficiency", p_max=100, p_min=0, x_max_scalar=2
)


# @dataclass
# class CompetitionPoints(object):
#     """
#     Points scored in each event at Formula Student.

#     Attributes:
#         acceleration (float): Points scored in the acceleration event.
#         skidpad (float): Points scored in the skidpad event.
#         autocross (float): Points scored in the autocross event.
#         endurance (float): Points scored in the endurance event.
#     """

#     acceleration: float
#     skidpad: float
#     autocross: float
#     endurance: float

#     @property
#     def total(self) -> float:
#         return (
#             self.acceleration + self.skidpad + self.autocross + self.endurance
#         )

#     def plot_pie_chart(self) -> None:
#         """
#         Plot a pie chart of points scored in each event.
#         """
#         points = {
#             "Acceleration": self.acceleration,
#             "Skidpad": self.skidpad,
#             "Autocross": self.autocross,
#             "Endurance": self.endurance,
#         }
#         plt.pie(list(points.values()), labels=list(points.keys()))
#         plt.show()


# def calculate_points(
#     results: CompetitionResults,
#     data: CompetitionData = CompetitionData.get_dataset("FSUK 2025"),
#     formulae: PointsFunctions = FSUKPointsFunctions(),
# ) -> CompetitionPoints:
#     """
#     Calculate points scored in each event at Formula Student.

#     Args:
#         results (CompetitionResults):
#             The results of a competition simulation.
#         data (Optional[CompetitionData]):
#             The competition data to use for calculating points.
#         formulae (PointsFunctions, optional):
#             The points formulae to use.

#     Returns:
#         points (CompetitionPoints): The points scored in each event.
#     """
#     points = CompetitionPoints(
#         acceleration=formulae.calculate_acceleration_points(
#             t_team=results.acceleration.total_time,
#             t_min=data.acceleration_t_min,
#         ),
#         skidpad=formulae.calculate_skidpad_points(
#             t_team=results.skidpad.total_time / 2, t_min=data.skidpad_t_min
#         ),
#         autocross=formulae.calculate_autocross_points(
#             t_team=results.autocross.total_time, t_min=data.autocross_t_min
#         ),
#         endurance=formulae.calculate_endurance_points(
#             t_team=results.endurance.total_time, t_min=data.endurance_t_min
#         ),
#     )
#     return points

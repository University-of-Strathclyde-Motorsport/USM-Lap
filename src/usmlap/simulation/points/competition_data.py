"""
This module contains code for handling competition data.
"""


class CompetitionData(object):
    """
    Scores from Formula Student competition,
    used to calculate points scored at competition.

    Attributes:
        acceleration_t_min (float): The minimum time for the acceleration event.
        skidpad_t_min (float): The minimum time for the skidpad event.
        autocross_t_min (float): The minimum time for the autocross event.
        endurance_t_min (float): The minimum time for the endurance event.
    """

    acceleration_t_min = 4.324
    skidpad_t_min = 5.826
    autocross_t_min = 55.423
    endurance_t_min = 1934.4

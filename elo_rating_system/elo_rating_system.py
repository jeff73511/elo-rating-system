from itertools import count
from pydantic import NonNegativeFloat, PositiveInt, NonNegativeInt
from pydantic.dataclasses import dataclass
from typing import Tuple


# import os
# os.chdir(r"C:\\Users\\c.chen\\PycharmProjects\\elo-rating-system\\elo_rating_system")
# import pandas as pd
#
# df = pd.read_csv("UEFA_Womens_EURO_2017.csv")


def actual_score_win_draw_loss(team1_score: int, team2_score: int):
    if team1_score > team2_score:
        return 1
    elif team1_score < team2_score:
        return 0
    else:
        return 1 / 2


def actual_score_proportional(team1_score: int, team2_score: int):
    return (team1_score + 1) / (team1_score + team2_score + 2)


def expected_score(
        home_rating: float, away_rating: float, home_advantage: NonNegativeFloat = 0):
    return 1 / (1 + 10 ** ((away_rating - home_rating - home_advantage) / 400))


@dataclass
class Team:
    name: str
    rating: float = 1000

    def __str__(self):
        return (
            f"We are team {self.name} and our current Elo rating is {self.rating}."
        )


@dataclass
class Match:
    team1: Team
    team2: Team
    home_team: Team = None
    home_advantage: NonNegativeInt = 100
    k_factor: PositiveInt = 32
    team1_score: NonNegativeInt
    team2_score: NonNegativeInt

    _match_id_counter = count(1)

    def __post_init__(self):
        if self.home_team not in (self.team1, self.team2, None):
            raise ValueError(f"Home team must be {self.team1}, {self.team2} or None")

        self.match_id = next(self._match_id_counter)

    def calculate_ratings(self, actual_score_option: str = "win_draw_loss") -> Tuple[float, float]:

        if actual_score_option == "win_draw_loss":
            team1_actual_score = actual_score_win_draw_loss(self.team1_score, self.team2_score)
        elif actual_score_option == "proportional":
            team1_actual_score = actual_score_proportional(self.team1_score, self.team2_score)
        else:
            raise ValueError("Actual score option must be either 'proportional' or 'win_draw_loss'")
        team2_actual_score = 1 - team1_actual_score

        if self.home_team == self.team1:
            team1_expected_score = expected_score(self.team1_rating, self.team2_rating,
                                                  self.home_advantage)
        elif self.home_team == self.team2:
            team1_expected_score = expected_score(self.team2_rating, self.team1_rating,
                                                  self.home_advantage)
        else:
            team1_expected_score = expected_score(self.team1_rating, self.team2_rating)
        team2_expected_score = 1 - team1_expected_score

        team1_new_rating = self.team1.rating + self.k_factor * (team1_actual_score - team1_expected_score)
        team2_new_rating = self.team2.rating + self.k_factor * (team2_actual_score - team2_expected_score)

        self.team1.rating = team1_new_rating
        self.team2.rating = team2_new_rating

        return team1_new_rating, team2_new_rating

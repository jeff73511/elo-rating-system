from itertools import count
import pandas as pd
from pydantic import NonNegativeFloat, PositiveInt, NonNegativeInt, PositiveFloat
from pydantic.dataclasses import dataclass
from typing import List


def actual_score_win_draw_loss(team1_score: int, team2_score: int) -> NonNegativeFloat:
    """Calculates the actual score of a match between two teams based on their scores.

    Args:
        team1_score: Score of the first team.
        team2_score: Score of the second team.
    Returns:
        Actual score of the match, either 1 for a win, 0 for a loss, or 0.5 for a draw.
    """

    if team1_score > team2_score:
        return 1
    elif team1_score < team2_score:
        return 0
    else:
        return 1 / 2


def actual_score_proportional(team1_score: int, team2_score: int) -> NonNegativeFloat:
    """Calculates the actual score of a match between two teams based on their scores proportionally.

    Args:
        team1_score: Score of the first team.
        team2_score: Score of the second team.
    Returns:
        Actual score of the match, a value between 0 and 1.
    """

    return (team1_score + 1) / (team1_score + team2_score + 2)


def expected_score(
        home_rating: float, away_rating: float, home_advantage: NonNegativeFloat) -> PositiveFloat:
    """Calculates the expected score for a team in a match based on their ratings and the home advantage.

    Args:
        home_rating: Rating of the home team.
        away_rating: Rating of the away team.
        home_advantage: Home advantage for the home team.
    Returns:
        Expected score for the home team, a value between 0 and 1.
    """

    return 1 / (1 + 10 ** ((away_rating - home_rating - home_advantage) / 400))


ACTUAL_SCORE_FUNCTIONS = {
    "win_draw_loss": actual_score_win_draw_loss,
    "proportional": actual_score_proportional
}


@dataclass
class Team:
    """Represents a team.

    Attributes:
        name: The name of the team.
        rating: The Elo rating of the team (default 1000).
    """

    name: str
    rating: float = 1000

    def __str__(self):
        """Returns a string representation of the team.

        Returns:
            str: A string representing the team and its current rating.
        """

        return (
            f"We are team {self.name} and our current Elo rating is {self.rating}."
        )


@dataclass
class Match:
    """Represents a match between two teams.

    Attributes:
        team1: The first team.
        team2: The second team.
        k_factor: The K-factor for Elo rating update (default 32).
        home_team: The home team. Default is None.
        home_advantage: The home advantage for the home team (default 0).
        team1_score: The score of team 1 (default None).
        team2_score: The score of team 2 (default None).
        team1_rating_updated: The updated rating of team 1 after the match (default None).
        team2_rating_updated: The updated rating of team 2 after the match (default None).
        ratings_updated_after_match: Indicates whether the ratings have been updated after the match (default False).
    """

    team1: Team
    team2: Team
    k_factor: PositiveInt = 32
    home_team: Team = None
    home_advantage: NonNegativeInt = 0
    team1_score: NonNegativeInt = None
    team2_score: NonNegativeInt = None
    team1_rating_updated: float = None
    team2_rating_updated: float = None

    _match_id_counter = count(1)

    ratings_updated_after_match: bool = False

    def __post_init__(self):
        """Performs post-initialization tasks for the Match object."""

        if self.home_team not in (self.team1, self.team2, None):
            raise ValueError(f"Home team must be {self.team1}, {self.team2} or None")

        self.match_id = next(self._match_id_counter)

    def update_ratings(self, actual_score_option: str) -> None:
        """Updates the ratings of the teams based on the match result and Elo algorithm.

        Args:
            actual_score_option: The option to determine the actual score calculation method.
        """

        if self.ratings_updated_after_match:
            print("The match already played.")
            return

        team1_actual_score = ACTUAL_SCORE_FUNCTIONS[actual_score_option](self.team1_score, self.team2_score)
        team2_actual_score = 1 - team1_actual_score

        if self.home_team == self.team1:
            team1_expected_score = expected_score(self.team1.rating, self.team2.rating, self.home_advantage)
        elif self.home_team == self.team2:
            team1_expected_score = expected_score(self.team2.rating, self.team1.rating, self.home_advantage)
        else:
            team1_expected_score = expected_score(self.team1.rating, self.team2.rating, 0)
        team2_expected_score = 1 - team1_expected_score

        team1_new_rating = self.team1.rating + self.k_factor * (team1_actual_score - team1_expected_score)
        team2_new_rating = self.team2.rating + self.k_factor * (team2_actual_score - team2_expected_score)

        self.team1.rating, self.team2.rating = team1_new_rating, team2_new_rating
        self.team1_rating_updated, self.team2_rating_updated = self.team1.rating, self.team2.rating

        self.ratings_updated_after_match = True


@dataclass
class Tournament:
    teams: List[Team]
    matches: List[Match]
    home_team_country: str = "NL"
    home_advantage: NonNegativeInt = 0
    k_factor: PositiveInt = 32

    def add_match(self, team1_name: str, team2_name: str, team1_score: NonNegativeInt, team2_score: NonNegativeInt,
                  actual_score_option: str = "win_draw_loss") -> None:
        """Adds a match to the tournament by manually entering the details.

        Args:
            team1_name: Name of the first team.
            team2_name: Name of the second team.
            team1_score: Score of the first team.
            team2_score: Score of the second team.
            actual_score_option: Option for calculating the actual score (default "win_draw_loss").
        """
        team1 = next((team for team in self.teams if team.name == team1_name.upper()), None)
        if team1 is None:
            team1 = Team(name=team1_name)
            self.teams.append(team1)

        team2 = next((team for team in self.teams if team.name == team2_name.upper()), None)
        if team2 is None:
            team2 = Team(name=team2_name)
            self.teams.append(team2)

        home_team = next((team for team in [team1, team2] if team.name == self.home_team_country.upper()), None)

        match = Match(team1=team1, team2=team2, home_team=home_team, home_advantage=self.home_advantage,
                      k_factor=self.k_factor, team1_score=team1_score, team2_score=team2_score)

        match.update_ratings(actual_score_option)

        self.matches.append(match)

    def add_matches_from_csv(self, csv_file: str, actual_score_option: str = "win_draw_loss") -> None:
        """Adds matches to the tournament by reading a CSV file.

        Arg:
            csv_file: Path to the CSV file containing match data.
            actual_score_option: Option for calculating the actual score (default "win_draw_loss").
        """

        df = pd.read_csv(csv_file)

        for i, row in df.iterrows():
            team1_name = row.TEAM1
            team2_name = row.TEAM2
            team1_score = row.TEAM1_SCORE
            team2_score = row.TEAM2_SCORE

            self.add_match(team1_name, team2_name, team1_score, team2_score, actual_score_option)


# import os
# os.chdir(r"C:\\Users\\c.chen\\PycharmProjects\\elo-rating-system\\elo_rating_system")
# import pandas as pd
#
# df = pd.read_csv("UEFA_Womens_EURO_2017.csv")
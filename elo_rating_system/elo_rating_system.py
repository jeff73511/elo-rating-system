from itertools import count
import pandas as pd
from pydantic import NonNegativeFloat, PositiveInt, NonNegativeInt, PositiveFloat
from pydantic.dataclasses import dataclass
from typing import List


# import os
# os.chdir(r"C:\\Users\\c.chen\\PycharmProjects\\elo-rating-system\\elo_rating_system")
# import pandas as pd
#
# df = pd.read_csv("UEFA_Womens_EURO_2017.csv")


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
        home_advantage: Home advantage for the home team (defaults 0).
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
        if self.home_team not in (self.team1, self.team2, None):
            raise ValueError(f"Home team must be {self.team1}, {self.team2} or None")

        self.match_id = next(self._match_id_counter)

    def update_ratings(self, actual_score_option) -> None:

        if self.match_played:
            print("The match already played.")
            return

        team1_actual_score = ACTUAL_SCORE_FUNCTIONS[actual_score_option](self.team1_score, self.team2_score)
        team2_actual_score = 1 - team1_actual_score

        if self.home_team == self.team1:
            team1_expected_score = expected_score(self.team1_rating, self.team2_rating, self.home_advantage)
        elif self.home_team == self.team2:
            team1_expected_score = expected_score(self.team2_rating, self.team1_rating, self.home_advantage)
        else:
            team1_expected_score = expected_score(self.team1_rating, self.team2_rating, 0)
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
    home_advantage: NonNegativeInt = 100,
    k_factor: PositiveInt = 32

    @classmethod
    def from_dataframe(cls,
                       csv_file_path: str,
                       actual_score_option: str = "win_draw_loss"
                       ) -> "Tournament":
        df = pd.read_csv(csv_file_path)

        team_names = set(df["TEAM1"]).union(set(df["TEAM2"]))
        teams = [Team(name) for name in team_names]

        # cls.matches = []
        for i, row in df.iter:
            team1 = next(team for team in teams if team.name == row["TEAM1"])
            team2 = next(team for team in teams if team.name == row["TEAM1"])
            home_team = next((team for team in [team1, team2] if team.name == cls.home_team_country), None)
            team1_score = row["TEAM1_SCORE"]
            team2_score = row["TEAM2_SCORE"]
            match = Match(team1=team1, team2=team2, home_team=home_team, home_advantage=cls.home_advantage,
                          k_factor=cls.k_factor, team1_score=team1_score, team2_score=team2_score)
            match.update_ratings(actual_score_option)
            cls.matches.append(match)

        return cls()

    def add_match(self, team1_name: str, team2_name: str, team1_score: NonNegativeInt, team2_score: NonNegativeInt,
                  actual_score_option: str = "win_draw_loss") -> None:
        team1 = next((team for team in self.teams if team.name == team1_name.upper()), Team(team1_name))
        team2 = next((team for team in self.teams if team.name == team2_name.upper()), Team(team2_name))
        home_team = next((team for team in [team1, team2] if team.name == self.home_team_country.upper()), None)
        match = Match(team1=team1, team2=team2, home_team=home_team, home_advantage=self.home_advantage,
                      k_factor=self.k_factor, team1_score=team1_score, team2_score=team2_score)

        match.update_ratings(actual_score_option)
        self.matches.append(match)

# tournament = Tournament.from_dataframe(df)
# print(tournament.teams)  # [Team(name='Team B', rating=1000), Team(name='Team A', rating=1000)]
# print(tournament.matches)  # [Match(...), Match(...)]
# tournament.update_ratings()
# print(tournament.teams)  # [Team(name='Team B', rating=988.6858166872627), Team(name='Team A', rating=1011.3141833127373)]

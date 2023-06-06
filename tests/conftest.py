import pytest
from elo_rating_system.elo_rating_system import Team, Match, Tournament
import csv


TEAM1_SCORE = 2
TEAM2_SCORE = 1


@pytest.fixture
def team1():
    return Team(name="Team A", rating=1000.0)


@pytest.fixture
def team2():
    return Team(name="Team B", rating=1000.0)


@pytest.fixture
def team1_score():
    return TEAM1_SCORE


@pytest.fixture
def team2_score():
    return TEAM2_SCORE


@pytest.fixture
def match(team1, team2, team1_score, team2_score):
    return Match(team1=team1, team2=team2, team1_score=team1_score, team2_score=team2_score)


@pytest.fixture
def tournament(team1, team2, match):
    return Tournament(teams=[team1, team2], matches=[match])


@pytest.fixture
def csv_file_fixture(tmp_path):
    csv_file_path = tmp_path / "matches.csv"

    csv_data = [
        ["TEAM1", "TEAM2", "TEAM1_SCORE", "TEAM2_SCORE"],
        ["Team C", "Team D", 3, 1],
        ["Team E", "Team F", 0, 2],
        ["Team G", "Team H", 2, 2]
    ]

    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)

    return csv_file_path

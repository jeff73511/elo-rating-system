import pytest
from elo_rating_system.elo_rating_system import Team, Match


@pytest.fixture
def teams():
    team1 = Team(name="Team 1", rating=1000)
    team2 = Team(name="Team 2", rating=1000)
    return team1, team2

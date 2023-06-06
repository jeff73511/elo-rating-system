import itertools
import pytest
from elo_rating_system.elo_rating_system import (
    actual_score_win_draw_loss,
    actual_score_proportional,
    expected_score,
    Team,
    Match
)


def test_actual_score_win_draw_loss():
    assert actual_score_win_draw_loss(2, 1) == 1
    assert actual_score_win_draw_loss(1, 2) == 0
    assert actual_score_win_draw_loss(1, 1) == 0.5


def test_actual_score_proportional():
    assert actual_score_proportional(2, 1) == 0.6
    assert actual_score_proportional(1, 2) == 0.4
    assert actual_score_proportional(1, 1) == 0.5


def test_expected_score():
    home_rating = 1500
    away_rating = 1400
    home_advantage = 100
    expected = 0.7597
    assert expected_score(home_rating, away_rating, home_advantage) == pytest.approx(expected, abs=1e-4)


def test_team_str(team1):
    assert str(team1) == "We are team Team A and our current Elo rating is 1000.0."


def test_match_creation_with_invalid_home_team(team1, team2):
    with pytest.raises(ValueError):
        Match(team1=team1, team2=team2, home_team=Team(name="Invalid Team"))


def test_match_update_ratings(team1, team2, match):
    initial_team1_rating = match.team1.rating
    initial_team2_rating = match.team2.rating
    match.update_ratings(actual_score_option="win_draw_loss")
    assert match.ratings_updated_after_match
    assert match.team1_rating_updated != initial_team1_rating
    assert match.team2_rating_updated != initial_team2_rating
    assert match.team1_rating_updated == match.team1.rating == team1.rating
    assert match.team2_rating_updated == match.team2.rating == team2.rating


def test_tournament_add_match(tournament):
    team1_name = "Team C"
    team2_name = "Team D"
    team1_score = 3
    team2_score = 0
    teams_count = len(tournament.teams)
    matches_count = len(tournament.matches)

    tournament.add_match(
        team1_name=team1_name,
        team2_name=team2_name,
        team1_score=team1_score,
        team2_score=team2_score,
    )

    assert len(tournament.teams) == teams_count + 2
    assert len(tournament.matches) == matches_count + 1
    assert tournament.matches[-1].team1.name == team1_name
    assert tournament.matches[-1].team2.name == team2_name
    assert tournament.matches[-1].team1_score == team1_score
    assert tournament.matches[-1].team2_score == team2_score
    assert tournament.matches[-1].ratings_updated_after_match

    for team, match in itertools.product(tournament.teams, tournament.matches):
        if match.team1 == team:
            assert match.team1_rating_updated == match.team1.rating == team.rating
        if match.team2 == team:
            assert match.team2_rating_updated == match.team2.rating == team.rating


def test_tournament_add_matches_from_csv(tournament, csv_file_fixture):
    tournament.add_matches_from_csv(csv_file_fixture)

    assert len(tournament.matches) == 4

    last_match = tournament.matches[-1]
    assert last_match.team1.name == "Team G"
    assert last_match.team2.name == "Team H"
    assert last_match.team1_score == 2
    assert last_match.team2_score == 2
    assert last_match.ratings_updated_after_match

    for team, match in itertools.product(tournament.teams, tournament.matches):
        if match.team1 == team:
            assert match.team1_rating_updated == match.team1.rating == team.rating
        if match.team2 == team:
            assert match.team2_rating_updated == match.team2.rating == team.rating

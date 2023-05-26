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
    assert actual_score_proportional(2, 1) == 0.75
    assert actual_score_proportional(1, 2) == 0.4
    assert actual_score_proportional(1, 1) == 0.5


def test_expected_score():
    home_rating = 1500
    away_rating = 1400
    home_advantage = 100
    expected = 0.7597
    assert expected_score(home_rating, away_rating, home_advantage) == pytest.approx(expected, abs=1e-4)

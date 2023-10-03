import pytest
import numpy as np
import pandas as pd
from src.playerBpm import BpmCalculator


@pytest.fixture
def mock_data():
    # Season and Game team metrics
    season_df = pd.read_csv("data/texas_tech_bpm_test_data_season_level.csv")
    season_df.rename({"Unnamed: 1": "Player"}, axis=1, inplace=True)
    game_df = pd.read_csv("data/texas_tech_bpm_test_data_game_level.csv")
    game_df.rename({"Starters": "Player"}, axis=1, inplace=True)
    season_team_metrics = {
        "Pace": 66,
        "Team Pts": 2765,
        "Team FGA": 2110,
        "Team FTA": 694,
        "Tm Pts/TSA": 1.13,
        "Baseline Pts/TSA": 1.0,
        "Total Minutes": 7652,
        "Team TRB": 1209,
        "Team Steal": 278,
        "Team PF": 663,
        "Team AST": 518,
        "Team BLK": 186,
        "Team Games": 38,
    }

    general_game_stats = {
        "Team_A_Score": 75,
        "Team_B_Score": 69,
        "Team_A_Adj_OE": 115.9,
        "Team_A_Adj_DE": 86.4,
        "Team_B_Adj_OE": 124.4,
        "Team_B_Adj_DE": 91,
        "Team_A_OE": 105.17,
        "Team_B_OE": 96.757,
    }

    game_team_metrics = {
        "Pace": 71.3128,
        "Mins": 200,
        "Pts": 75,
        "FGA": 57,
        "FTA": 19,
        "Tm Pts/TSA": 1.14,
        "Baseline Pts/TSA": 1.0,
    }

    jarrett_culver_data = {
        "MP": 32,
        "Pts/TSA": 1.08,
        "Season TSA": 650,
        "Game Pts/TSA": 0.83,
        "Game TSA": 22.8,
    }

    bpm_calculator = BpmCalculator(
        season_df, game_df, season_team_metrics, game_team_metrics
    )
    player_season = season_df[season_df["Player"] == "Jarrett Culver"].iloc[0]
    player_game = game_df[game_df["Player"] == "Jarrett Culver"].iloc[0]

    game_level_p100p = bpm_calculator.calculate_p_100_p_stats(
        player_game, game_team_metrics
    )
    return (
        bpm_calculator,
        player_season,
        player_game,
        season_team_metrics,
        game_team_metrics,
        season_df,
        game_df,
        game_level_p100p,
        general_game_stats,
    )


def test_calculate_pts_tsa(mock_data):
    (
        bpm_calculator,
        player_season,
        player_game,
        season_team_metrics,
        game_team_metrics,
        season_df,
        _,
        _,
        _,
    ) = mock_data

    pts_tsa = bpm_calculator.calculate_pts_tsa(player_season)
    assert pts_tsa == pytest.approx(1.08, 0.01)

    pts_tsa_game = bpm_calculator.calculate_pts_tsa(player_game)
    assert pts_tsa_game == pytest.approx(0.83, 0.01)


def test_calculate_adj_pts(mock_data):
    (
        bpm_calculator,
        player_season,
        player_game,
        season_team_metrics,
        game_team_metrics,
        _,
        _,
        _,
        _,
    ) = mock_data

    adj_pts_season = bpm_calculator.calculate_adj_pts(
        player_season, season_team_metrics
    )
    assert adj_pts_season == pytest.approx(617.3, 0.1)

    adj_pts_game = bpm_calculator.calculate_adj_pts(player_game, game_team_metrics)
    assert adj_pts_game == pytest.approx(
        15.9, 0.1
    )  # Replace 0.0 with the expected value


def test_calculate_possessions(mock_data):
    (
        bpm_calculator,
        player_season,
        player_game,
        season_team_metrics,
        game_team_metrics,
        season_df,
        _,
        _,
        _,
    ) = mock_data

    possessions = bpm_calculator.calculate_possessions(
        player_season, season_team_metrics
    )
    assert possessions == pytest.approx(2036, 0.01)

    possessions = bpm_calculator.calculate_possessions(player_game, game_team_metrics)
    assert possessions == pytest.approx(62.4, 0.01)


def test_calculate_thresh_pts(mock_data):
    #     bpm_calculator = mock_data
    (
        bpm_calculator,
        player_season,
        player_game,
        season_team_metrics,
        game_team_metrics,
        season_df,
        _,
        _,
        _,
    ) = mock_data

    thresh_pts = bpm_calculator.calculate_thresh_pts(player_season, season_team_metrics)
    assert thresh_pts == pytest.approx(184, 0.01)


def test_calculate_position(mock_data):
    (
        bpm_calculator,
        player_season,
        player_game,
        season_team_metrics,
        game_team_metrics,
        season_df,
        _,
        _,
        _,
    ) = mock_data

    # Assuming the method calculate_position is implemented in BpmCalculator class
    position_vals = bpm_calculator.calculate_position(season_df, season_team_metrics)

    assert len(position_vals) == len(season_df)
    assert position_vals["Jarrett Culver"] == pytest.approx(2.8, 0.01)
    assert position_vals["Malik Ondigo"] == pytest.approx(4.6, 0.01)


def test_calculate_offensive_role(mock_data):
    (
        bpm_calculator,
        player_season,
        player_game,
        season_team_metrics,
        game_team_metrics,
        season_df,
        _,
        _,
        _,
    ) = mock_data

    # Assuming the method calculate_position is implemented in BpmCalculator class
    offensive_roles = bpm_calculator.calculate_offensive_role(
        season_df, season_team_metrics
    )

    assert len(offensive_roles) == len(season_df)
    # Excel Sheet Rounds to 0.1.......
    assert offensive_roles["Jarrett Culver"] == pytest.approx(1.5, 0.1)
    assert offensive_roles["Davide Moretti"] == pytest.approx(2.1, 0.1)
    assert offensive_roles["Malik Ondigo"] == pytest.approx(5.0, 0.1)


# # Define the test for the calculate_scoring method
def test_calculate_scoring(mock_data):
    (
        bpm_calculator,
        player_season,
        player_game,
        season_team_metrics,
        game_team_metrics,
        season_df,
        game_df,
        game_level_p100p,
        _,
    ) = mock_data

    scoring = bpm_calculator.calculate_scoring(player_season, game_level_p100p)
    # Scoring for Jarrett Culver
    assert scoring == pytest.approx(1.8, 0.1)

    # Scoring for Matt Mooney
    player_season = season_df[season_df["Player"] == "Matt Mooney"].iloc[0]
    player_game = game_df[game_df["Player"] == "Matt Mooney"].iloc[0]
    game_level_p100p = bpm_calculator.calculate_p_100_p_stats(
        player_game, game_team_metrics
    )
    bpm_calculator = BpmCalculator(
        season_df, game_df, season_team_metrics, game_team_metrics
    )
    scoring = bpm_calculator.calculate_scoring(player_season, game_level_p100p)
    assert scoring == pytest.approx(6.4, 0.1)


def test_calculate_ballhandling(mock_data):
    (
        bpm_calculator,
        player_season,
        _,
        _,
        _,
        _,
        _,
        game_level_p100p,
        _,
    ) = mock_data

    ball_handling = bpm_calculator.calculate_ballhandling(
        player_season, game_level_p100p
    )
    assert ball_handling == pytest.approx(-2.1, 0.1)


def test_calculate_rebounding(mock_data):
    (
        bpm_calculator,
        player_season,
        _,
        _,
        _,
        _,
        _,
        game_level_p100p,
        _,
    ) = mock_data

    rebounding = bpm_calculator.calculate_rebounding(player_season, game_level_p100p)
    assert rebounding == pytest.approx(2.0, 0.1)


def test_calculate_defense(mock_data):
    (
        bpm_calculator,
        player_season,
        _,
        _,
        _,
        _,
        _,
        game_level_p100p,
        _,
    ) = mock_data

    defense = bpm_calculator.calculate_defense(player_season, game_level_p100p)
    assert defense == pytest.approx(5.7, 0.1)


def test_calculate_position_adjustment(mock_data):
    (
        bpm_calculator,
        player_season,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = mock_data

    pos_adj = bpm_calculator.calculate_position_adjustment(player_season)
    assert pos_adj == pytest.approx(-2.2, 0.1)


def test_calculate_raw_bpm(mock_data):
    (
        bpm_calculator,
        _,
        player_game,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = mock_data

    raw_bpm = bpm_calculator.calculate_raw_bpm(player_game)
    assert raw_bpm == pytest.approx(5.2, 0.1)


def test_calculate_team_adjustment(mock_data):
    (
        bpm_calculator,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
        general_game_stats,
    ) = mock_data

    team_adjustment = bpm_calculator.calculate_team_adjustment(
        general_game_stats, 41.88
    )["team_adjustment"]
    assert team_adjustment == pytest.approx(-1.16, 0.1)


def test_calculate_bpm(mock_data):
    (
        bpm_calculator,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
        general_game_stats,
    ) = mock_data

    players = bpm_calculator.calculate_bpm(general_game_stats)["box"]
    assert players["Jarrett Culver"] == pytest.approx(4.1, 0.1)
    assert players["Matt Mooney"] == pytest.approx(11.3, 0.1)
    assert players["Davide Moretti"] == pytest.approx(4.1, 0.1)
    assert players["Tariq Owens"] == pytest.approx(9.9, 0.1)
    assert players["Norense Odiase"] == pytest.approx(5.1, 0.1)
    assert players["Brandone Francis"] == pytest.approx(2.5, 0.1)
    assert players["Kyler Edwards"] == pytest.approx(14.8, 0.1)
    assert players["Deshawn Corprew"] == pytest.approx(8.9, 0.1)


def test_calculate_obpm(mock_data):
    (
        bpm_calculator,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
        general_game_stats,
    ) = mock_data

    players = bpm_calculator.calculate_bpm(general_game_stats, bpm_type="offense")[
        "box"
    ]
    assert players["Jarrett Culver"] == pytest.approx(1.6, 0.1)
    assert players["Matt Mooney"] == pytest.approx(4.9, 0.1)
    assert players["Davide Moretti"] == pytest.approx(1.3, 0.1)
    assert players["Tariq Owens"] == pytest.approx(2.6, 0.1)
    assert players["Norense Odiase"] == pytest.approx(2.7, 0.1)
    assert players["Brandone Francis"] == pytest.approx(-0.2, 0.1)
    assert players["Kyler Edwards"] == pytest.approx(9.4, 0.1)
    assert players["Deshawn Corprew"] == pytest.approx(0.6, 0.1)


def test_calculate_obpm(mock_data):
    (
        bpm_calculator,
        _,
        _,
        _,
        game_team_metrics,
        _,
        _,
        _,
        general_game_stats,
    ) = mock_data

    players = bpm_calculator.calculate_all_stats(general_game_stats, game_team_metrics)

    assert players["Jarrett Culver"]["NET"] == pytest.approx(-1.5, 0.1)
    assert players["Matt Mooney"]["NET"] == pytest.approx(3.1, 0.1)
    assert players["Davide Moretti"]["NET"] == pytest.approx(-1.4, 0.1)

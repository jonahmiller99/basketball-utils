import math
import numpy as np


class BpmCalculator:
    # BPM Constants and Coefficients
    BPM_COEFFICIENTS = {
        "Pos_1_Adj_Pt": 0.860,
        "Pos_1_FGA": -0.560,
        "Pos_1_FTA": -0.266,
        "Pos_1_3FG_Bonus": 0.389,
        "Pos_1_AST": 0.580,
        "Pos_1_TO": -0.964,
        "Pos_1_ORB": 0.613,
        "Pos_1_DRB": 0.116,
        "Pos_1_TRB": 0.000,
        "Pos_1_STL": 1.369,
        "Pos_1_BLK": 1.327,
        "Pos_1_PF": -0.367,
        "Pos_5_Adj_Pt": 0.860,
        "Pos_5_FGA": -0.780,
        "Pos_5_FTA": -0.371,
        "Pos_5_3FG_Bonus": 0.389,
        "Pos_5_AST": 1.034,
        "Pos_5_TO": -0.964,
        "Pos_5_ORB": 0.181,
        "Pos_5_DRB": 0.181,
        "Pos_5_TRB": 0.000,
        "Pos_5_STL": 1.008,
        "Pos_5_BLK": 0.703,
        "Pos_5_PF": -0.367,
    }

    OBPM_COEFFICIENTS = {
        "Pos_1_Adj_Pt": 0.605,
        "Pos_1_FGA": -0.330,
        "Pos_1_FTA": -0.157,
        "Pos_1_3FG_Bonus": 0.477,
        "Pos_1_AST": 0.476,
        "Pos_1_TO": -0.579,
        "Pos_1_ORB": 0.606,
        "Pos_1_DRB": -0.112,
        "Pos_1_TRB": 0.000,
        "Pos_1_STL": 0.177,
        "Pos_1_BLK": 0.725,
        "Pos_1_PF": -0.439,
        "Pos_5_Adj_Pt": 0.605,
        "Pos_5_FGA": -0.472,
        "Pos_5_FTA": -0.224,
        "Pos_5_3FG_Bonus": 0.477,
        "Pos_5_AST": 0.476,
        "Pos_5_TO": -0.882,
        "Pos_5_ORB": 0.422,
        "Pos_5_DRB": 0.103,
        "Pos_5_TRB": 0.000,
        "Pos_5_STL": 0.294,
        "Pos_5_BLK": 0.097,
        "Pos_5_PF": -0.439,
    }

    BPM_POSITION_CONSTANTS = {
        "Pos_1": -0.818,
        "Pos_3": 0,
        "Pos_5": 0,
        "Offensive_Role_Slope": 1.387,
    }

    OBPM_POSITION_CONSTANTS = {
        "Pos_1": -1.698,
        "Pos_3": 0,
        "Pos_5": 0,
        "Offensive_Role_Slope": 0.43,
    }

    OFFENSIVE_ROLE_COEFFICIENTS = {
        "Intercept": 6,
        "Perc_Of_AST": -6.642,
        "Perc_OF_ThreshPts": -8.544,
        "Pt_Threshold": -0.330,
        "Default_Pos": 4,
        "Min_Wt": 50,
    }

    # There are different coef for pre 1971, but that doesn't impact my data
    POSITION_COEFFICIENTS = {
        "Intercept": 2.130,
        "Perc_Of_TRB": 8.668,
        "Perc_Of_STL": -2.486,
        "Perc_Of_PF": 0.992,
        "Perc_Of_AST": -3.536,
        "Perc_Of_BLK": 1.667,
        "Min_Wt": 50,
    }

    POS_NUM = {
        "PG": 1,
        "SG": 2,
        "SF": 3,
        "PF": 4,
        "C": 5,
        "G-F": 2.5,
        "F-G": 2.5,
        "G": 1.5,
        "F": 3.5,
        "?": 3,
    }

    SEASON_STATS = {"AVG_RATING": 103.3}

    def __init__(self, season_df, game_df, season_team_metrics, game_team_metrics):
        self.season_df = season_df  # DataFrame containing season level data
        self.game_df = game_df  # DataFrame containing game level data
        self.season_team_metrics = season_team_metrics  # Seasonal team metrics
        self.game_team_metrics = game_team_metrics  # Game-specific team metrics

        # Dict with key = Name, Value = Position Coef
        # Season Level Coefficients, used to calculate per game BPM
        self.position = self.calculate_position(season_df, season_team_metrics)
        self.offensive_role = self.calculate_offensive_role(
            season_df, season_team_metrics
        )

        # Maybe reasign AVG_RATING on init

    def calculate_lead_bonus(self, general_game):
        avg_lead = (general_game["Team_A_Score"] - general_game["Team_B_Score"]) / 2

        lead_bonus = (0.35 / 2) * avg_lead

        return lead_bonus

    def calculate_team_adjustment(
        self, general_game, player_contribution_sum, bpm_type="default"
    ):
        lead_bonus = self.calculate_lead_bonus(general_game)

        team_a_lead_bonus = lead_bonus
        team_b_lead_bonus = -lead_bonus

        team_a_ORtg = general_game["Team_A_OE"]
        team_b_ORtg = general_game["Team_B_OE"]

        team_a_adj_ortg = team_a_ORtg + team_a_lead_bonus
        team_b_adj_ortg = team_b_ORtg + team_b_lead_bonus

        # bt_avg_rating .. I believe this is the avg_adj_oe?
        bt_avg_rating = self.SEASON_STATS["AVG_RATING"]

        Team_A_ORtg = general_game["Team_A_Adj_OE"] - bt_avg_rating
        Team_A_DRtg = bt_avg_rating - general_game["Team_A_Adj_DE"]

        Team_B_ORtg = general_game["Team_B_Adj_OE"] - bt_avg_rating
        Team_B_DRtg = bt_avg_rating - general_game["Team_B_Adj_DE"]

        Team_A_Game_ORtg = (team_a_adj_ortg - bt_avg_rating) / 2 + (
            (Team_A_ORtg + Team_B_DRtg) / 2
        )

        Team_A_Game_DRtg = (bt_avg_rating - team_b_adj_ortg) / 2 + (
            (Team_A_DRtg + Team_B_ORtg) / 2
        )

        if bpm_type == "offense":
            team_adjustment = (Team_A_Game_ORtg - player_contribution_sum) / 5
        else:
            team_adjustment = (
                (Team_A_Game_ORtg + Team_A_Game_DRtg) - player_contribution_sum
            ) / 5

        return {
            "team_adjustment": team_adjustment,
            "Team_A_ORtg": Team_A_ORtg,
            "Team_A_DRtg": Team_A_DRtg,
            "Team_B_ORtg": Team_B_ORtg,
            "Team_B_DRtg": Team_B_DRtg,
            "Rating_Total_A": Team_A_ORtg + Team_A_DRtg,
            "Rating_Total_B": Team_B_ORtg + Team_B_DRtg,
        }

    def calculate_raw_bpm(self, player, bpm_type="default"):
        game_level_p100p = self.calculate_p_100_p_stats(player, self.game_team_metrics)
        season_level_p100p = self.calculate_p_100_p_stats(
            player, self.season_team_metrics
        )

        scoring = self.calculate_scoring(player, game_level_p100p, bpm_type)
        ballhandling = self.calculate_ballhandling(player, game_level_p100p, bpm_type)
        rebounding = self.calculate_rebounding(player, game_level_p100p, bpm_type)
        defense = self.calculate_defense(player, game_level_p100p, bpm_type)
        position_adjustment = self.calculate_position_adjustment(player, bpm_type)

        return scoring + ballhandling + rebounding + defense + position_adjustment

    def calculate_p_100_p_stats(self, player, metrics):
        possessions = self.calculate_possessions(player, metrics)
        adj_pt = self.calculate_adj_pts(player, metrics=metrics)

        per_100_possessions = {
            "Adj_Pt": (adj_pt / possessions) * 100,
            "FGA": (player["FGA"] / possessions) * 100,
            "FTA": (player["FTA"] / possessions) * 100,
            "3FG": (player["3P"] / possessions) * 100,
            "AST": (player["AST"] / possessions) * 100,
            "TO": (player["TOV"] / possessions) * 100,
            "ORB": (player["ORB"] / possessions) * 100,
            "DRB": (player["DRB"] / possessions) * 100,
            "TRB": (player["TRB"] / possessions) * 100,
            "STL": (player["STL"] / possessions) * 100,
            "BLK": (player["BLK"] / possessions) * 100,
            "PF": (player["PF"] / possessions) * 100,
        }
        return per_100_possessions

    def calculate_scoring(self, player, game_level_p100p, bpm_type="default"):
        # Define the metrics for scoring
        metrics_bpm = ["Adj_Pt", "FGA", "FTA", "3FG_Bonus"]
        p100_metrics = ["Adj_Pt", "FGA", "FTA", "3FG"]

        # Compute the BPM values and p100p values
        bpm_values = [
            self.calculate_bpm_value(player, metric, bpm_type) for metric in metrics_bpm
        ]

        p100p_values = [game_level_p100p[metric] for metric in p100_metrics]

        return np.dot(bpm_values, p100p_values)

    def calculate_pts_tsa(self, player):
        # Why not just make player row in the season or game data?
        if player["TSA"] == 0:
            return 0

        return player["PTS"] / player["TSA"]

    def calculate_adj_pts(self, player, metrics):
        pts_tsa = self.calculate_pts_tsa(player)
        team_pts_tsa = metrics["Tm Pts/TSA"]
        baseline_pts_tsa = metrics["Baseline Pts/TSA"]
        tsa = player["TSA"]

        adj_pts = ((pts_tsa - team_pts_tsa) + baseline_pts_tsa) * tsa
        return adj_pts

    def calculate_possessions(self, player, metrics):
        mp = player["MP"]
        pace = metrics["Pace"]
        possessions = mp * pace / 40
        return possessions

    def calculate_thresh_pts(self, player, metrics):
        pts_tsa = self.calculate_pts_tsa(player)

        team_pts_tsa = metrics["Tm Pts/TSA"]
        tsa = player["TSA"]
        offensive_role_pt_threshold = self.OFFENSIVE_ROLE_COEFFICIENTS["Pt_Threshold"]

        thresh_pts = tsa * (pts_tsa - (team_pts_tsa + offensive_role_pt_threshold))
        return thresh_pts

    def calculate_ballhandling(self, player, game_level_p100p, bpm_type="default"):
        # Define the metrics for ballhandling
        metrics_bpm = ["AST", "TO"]

        bpm_values = [
            self.calculate_bpm_value(player, metric, bpm_type) for metric in metrics_bpm
        ]
        p100p_values = [game_level_p100p[metric] for metric in metrics_bpm]

        return np.dot(bpm_values, p100p_values)

    def calculate_rebounding(self, player, game_level_p100p, bpm_type="default"):
        # Define the metrics for rebounding
        metrics_bpm = ["ORB", "DRB", "TRB"]

        bpm_values = [
            self.calculate_bpm_value(player, metric, bpm_type) for metric in metrics_bpm
        ]
        p100p_values = [game_level_p100p[metric] for metric in metrics_bpm]

        return np.dot(bpm_values, p100p_values)

    def calculate_defense(self, player, game_level_p100p, bpm_type="default"):
        # Define the metrics for defense
        metrics_bpm = ["STL", "BLK", "PF"]

        bpm_values = [
            self.calculate_bpm_value(player, metric, bpm_type) for metric in metrics_bpm
        ]
        p100p_values = [game_level_p100p[metric] for metric in metrics_bpm]

        return np.dot(bpm_values, p100p_values)

    def calculate_offensive_role(self, season_df, season_metrics):
        # Initialize dictionary to store offensive role constants
        trim_one, trim_two, trim_three = [], [], []

        # Not efficient - revisit if this all takes too long
        thresh_pts = [
            self.calculate_thresh_pts(player, season_metrics)
            for _, player in season_df.iterrows()
        ]

        player_thresh_pts = dict(zip(list(season_df["Player"]), thresh_pts))
        total_thresh_pts = sum(thresh_pts)

        for _, player in season_df.iterrows():
            percent_min = player["MP"] / (season_metrics["Total Minutes"] / 5)
            percent_of_ast = (player["AST"] / season_metrics["Team AST"]) / percent_min
            precent_of_threshpts = (
                (player_thresh_pts[player["Player"]]) / total_thresh_pts / percent_min
            )

            est_off_role_one = (
                self.OFFENSIVE_ROLE_COEFFICIENTS["Intercept"]
                + self.OFFENSIVE_ROLE_COEFFICIENTS["Perc_Of_AST"] * percent_of_ast
                + self.OFFENSIVE_ROLE_COEFFICIENTS["Perc_OF_ThreshPts"]
                * precent_of_threshpts
            )

            or_min_adj_one = (
                est_off_role_one * season_metrics["Total Minutes"]
                + self.OFFENSIVE_ROLE_COEFFICIENTS["Default_Pos"]
                * self.OFFENSIVE_ROLE_COEFFICIENTS["Min_Wt"]
            ) / (
                season_metrics["Total Minutes"]
                + self.OFFENSIVE_ROLE_COEFFICIENTS["Min_Wt"]
            )

            trim_one.append(max(min(or_min_adj_one, 5), 1))

        or_tm_avg_1 = (
            np.dot(trim_one, season_df["MP"]) / season_metrics["Total Minutes"]
        )
        trim_two = [
            max(min(min_adj_1 - (or_tm_avg_1 - 3), 5), 1) for min_adj_1 in trim_one
        ]
        or_tm_avg_2 = (
            np.dot(trim_two, season_df["MP"]) / season_metrics["Total Minutes"]
        )
        trim_three = [
            max(min(min_adj_1 - (or_tm_avg_1 - 3) - (or_tm_avg_2 - 3), 5), 1)
            for min_adj_1 in trim_one
        ]
        tm_avg_3 = np.dot(trim_three, season_df["MP"]) / season_metrics["Total Minutes"]

        # Calculate final position constants for all players
        position_constants = [
            max(
                min(
                    min_adj_1 - (or_tm_avg_1 - 3) - (or_tm_avg_2 - 3) - (tm_avg_3 - 3),
                    5,
                ),
                1,
            )
            for min_adj_1 in trim_one
        ]

        offensive_role_lookup = dict(zip(list(season_df["Player"]), position_constants))
        return offensive_role_lookup

    def calculate_position(self, season_df, season_metrics):
        trim_one, trim_two, trim_three = [], [], []

        for _, player in season_df.iterrows():
            percent_min = player["MP"] / (season_metrics["Total Minutes"] / 5)
            percent_of_trb = (player["TRB"] / season_metrics["Team TRB"]) / percent_min
            percent_of_stl = (
                player["STL"] / season_metrics["Team Steal"]
            ) / percent_min
            percent_of_pf = (player["PF"] / season_metrics["Team PF"]) / percent_min
            percent_of_ast = (player["AST"] / season_metrics["Team AST"]) / percent_min
            percent_of_blk = (player["BLK"] / season_metrics["Team BLK"]) / percent_min

            est_pos_1 = self.POSITION_COEFFICIENTS["Intercept"] + np.dot(
                [
                    self.POSITION_COEFFICIENTS["Perc_Of_TRB"],
                    self.POSITION_COEFFICIENTS["Perc_Of_STL"],
                    self.POSITION_COEFFICIENTS["Perc_Of_PF"],
                    self.POSITION_COEFFICIENTS["Perc_Of_AST"],
                    self.POSITION_COEFFICIENTS["Perc_Of_BLK"],
                ],
                [
                    percent_of_trb,
                    percent_of_stl,
                    percent_of_pf,
                    percent_of_ast,
                    percent_of_blk,
                ],
            )

            if player["Position_On_Court"] in self.POS_NUM:
                pos_num = self.POS_NUM[player["Position_On_Court"]]
            else:
                pos_num = 3

            total_mp = player["MP"]

            min_adj_1 = (
                est_pos_1 * total_mp + pos_num * self.POSITION_COEFFICIENTS["Min_Wt"]
            ) / (total_mp + self.POSITION_COEFFICIENTS["Min_Wt"])

            trim_one.append(max(min(min_adj_1, 5), 1))

        # Calculate tm_avg_1, tm_avg_2, and tm_avg_3 based on all players
        tm_avg_1 = np.dot(trim_one, season_df["MP"]) / season_metrics["Total Minutes"]
        trim_two = [
            max(min(min_adj_1 - (tm_avg_1 - 3), 5), 1) for min_adj_1 in trim_one
        ]
        tm_avg_2 = np.dot(trim_two, season_df["MP"]) / season_metrics["Total Minutes"]
        trim_three = [
            max(min(min_adj_1 - (tm_avg_1 - 3) - (tm_avg_2 - 3), 5), 1)
            for min_adj_1 in trim_one
        ]
        tm_avg_3 = np.dot(trim_three, season_df["MP"]) / season_metrics["Total Minutes"]

        # Calculate final position constants for all players
        position_constants = [
            max(min(min_adj_1 - (tm_avg_1 - 3) - (tm_avg_2 - 3) - (tm_avg_3 - 3), 5), 1)
            for min_adj_1 in trim_one
        ]

        name_to_pos_constant = dict(zip(list(season_df["Player"]), position_constants))

        return name_to_pos_constant

    def calculate_position_adjustment(self, player, bpm_type="default"):
        player_name = player["Player"]
        position = self.position[player_name]
        pre_slope_adjustment = np.nan

        position_constants = self.BPM_POSITION_CONSTANTS

        if bpm_type == "offense":
            position_constants = self.OBPM_POSITION_CONSTANTS

        if position < 3:
            pre_slope_adjustment = (position - 1) / 2 * position_constants["Pos_3"] + (
                3 - position
            ) / 2 * position_constants["Pos_1"]
        else:
            pre_slope_adjustment = (position - 3) / 2 * position_constants["Pos_5"] + (
                5 - position
            ) / 2 * position_constants["Pos_3"]

        return pre_slope_adjustment + (
            position_constants["Offensive_Role_Slope"]
            * (self.offensive_role[player_name] - 3)
        )

    def calculate_bpm_value(self, player, metric, bpm_type="default"):
        player_name = player["Player"]
        coefficients = self.BPM_COEFFICIENTS

        if bpm_type == "offense":
            coefficients = self.OBPM_COEFFICIENTS

        pos_1_coef = coefficients[f"Pos_1_{metric}"]
        pos_5_coef = coefficients[f"Pos_5_{metric}"]

        position = self.position[player_name]
        offensive_role = self.offensive_role[player_name]

        if metric == "FGA" or metric == "FTA":
            return (5 - offensive_role) / 4 * pos_1_coef + (
                offensive_role - 1
            ) / 4 * pos_5_coef

        return (5 - position) / 4 * pos_1_coef + (position - 1) / 4 * pos_5_coef

    def calculate_bpm(self, general_game, bpm_type="default"):
        player_bpm = {}
        player_perc_min = {}

        total_contribution = 0
        for _, player in self.game_df.iterrows():
            raw_bpm = self.calculate_raw_bpm(player, bpm_type)

            percent_min = player["MP"] / (self.game_team_metrics["Mins"] / 5)

            contribution = percent_min * raw_bpm
            total_contribution += contribution

            player_bpm[player["Player"]] = raw_bpm
            player_perc_min[player["Player"]] = percent_min

        team_adjustment_obj = self.calculate_team_adjustment(
            general_game, total_contribution, bpm_type=bpm_type
        )
        team_adjustment = team_adjustment_obj["team_adjustment"]

        final_bpm = {key: value + team_adjustment for key, value in player_bpm.items()}

        return {
            "box": final_bpm,
            "team_adjustment_obj": team_adjustment_obj,
            "percent_min_lookup": player_perc_min,
        }

    def calculate_all_stats(self, general_game, game_team_metrics):
        bpm_res = self.calculate_bpm(general_game)

        bpms = bpm_res["box"]
        adjustment_obj = bpm_res["team_adjustment_obj"]
        perc_min_lookup = bpm_res["percent_min_lookup"]
        obpms = self.calculate_bpm(general_game, bpm_type="obpm")["box"]
        team_a_lead_bonus = self.calculate_lead_bonus(general_game)

        net = {}

        for player, bpm in bpms.items():
            net_adjustment = (
                (
                    bpm
                    - (team_a_lead_bonus / 5)
                    - (
                        (
                            adjustment_obj["Rating_Total_A"]
                            + adjustment_obj["Rating_Total_B"]
                        )
                        / 2
                    )
                    / 5
                )
                * perc_min_lookup[player]
                * (game_team_metrics["Pace"] / 100)
                * (game_team_metrics["Mins"] / 5 / 40)
            )

            net[player] = net_adjustment

        combined = {}
        for player in bpms.keys():
            combined[player] = {
                "BPM": bpms[player],
                "OBPM": obpms[player],
                "DBPM": bpms[player] - obpms[player],
                "NET": net[player],
            }

        return combined

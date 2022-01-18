import numpy as np
import pandas as pd
from pathlib import Path
from ast import literal_eval


def convert_scores_literal(score):
    try:
        return literal_eval(score)
    except:
        return f'Error: {score}'


def pts_diff(row):
    try:
        winner_pts = sum(row['winning_team_scores_lst'])
        loser_pts = sum(row['losing_team_scores_lst'])

        return winner_pts - loser_pts
    except:
        return np.nan


def game_pts_diff(win, lsr):
    winner_pts = np.array(win)
    loser_pts = np.array(lsr)

    return winner_pts - loser_pts


def preprocess_tour_data(csv_file):
    p = Path(csv_file).absolute()
    df = pd.read_csv(p)
    # Convert match date to datetime
    df['match_date_dt'] = pd.to_datetime(df['match_date'], errors='coerce')

    # Drop matches where score not present
    df = df[(df['losing_team_scores'] != 'n/a') & (df['winning_team_scores'] != 'n/a')]

    # Convert scores to list of int and get pts diff - Drop any rows with missing pts diff
    df['losing_team_scores_lst'] = df['losing_team_scores'].apply(lambda x: convert_scores_literal(x))
    df['winning_team_scores_lst'] = df['winning_team_scores'].apply(lambda x: convert_scores_literal(x))
    df['pts_diff'] = df.apply(lambda x: pts_diff(x), axis=1)

    df.dropna(subset=['pts_diff'], inplace=True)

    # Get score diff for winner of each game
    gme_pts_diff = []
    for row in df.itertuples():
        gme_pts_diff.append(game_pts_diff(row.winning_team_scores_lst, row.losing_team_scores_lst))

    df['gme_pts_diff'] = gme_pts_diff

    # Add a flag for doubles games
    df['Doubles'] = ~df.losing_team_p2.isna()

    df.sort_values(by=['match_date_dt'], ascending=True, inplace=True)

    df.reset_index(drop=True, inplace=True)

    return df


def briers_score(predictions, actual):
    return sum([(ft - ot) ** 2 for ft, ot in zip(predictions, actual)]) / len(predictions)


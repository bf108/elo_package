import numpy as np
import pandas as pd
import math
from elo import Elo
from player import Player


class ResultsTable:
    def __init__(self, df):
        """
        df - pd DataFrame of tournamenent results
        """
        # self.df = df.sort_values(by='match_date_dt', ascending=True)
        self.df = df.copy(deep=True)
        self.elo = Elo('test')
        self.player_dict = {2000000: Player('dummy', 2000000)}
        self.dummy_tsid = 2000001
        self.cold_start_threshold = 0

    def add_players_to_dict(self, row, df_results, kfactor=None, sd=None):
        """
        Adds all players from a row in the results table to player_dict, unless they already exist in player_dict
        Also, assigns temp tsid to players with missing tsid. This is a unique value starting at 2,000,001

        :param row: pd.Series - row of results df
        :param df_results: pd DataFrame - results df
        :param kfactor: float - kfactor to assign to player object
        :param sd: float - sd to assign to player object
        :return: None
        """
        row = row._asdict()
        if row['Doubles']:
            col_headings = [t + p + "_tsid" for t in ['winning_team_', 'losing_team_'] for p in ['p1', 'p2']]
        else:
            col_headings = [t + p + "_tsid" for t in ['winning_team_', 'losing_team_'] for p in ['p1']]

        tsids = [row[c] for c in col_headings]
        names = [row[c.split('_tsid')[0]] for c in col_headings]

        for ch, t, n in zip(col_headings, tsids, names):
            if np.isnan(t):
                self.player_dict[self.dummy_tsid] = Player(n, self.dummy_tsid, kfactor=kfactor, sd=sd)
                df_results.at[row['Index'], ch] = self.dummy_tsid
                self.dummy_tsid += 1
            else:
                if t not in self.player_dict:
                    self.player_dict[t] = Player(n, t, kfactor=kfactor, sd=sd)

    def get_unique_players_in_category(self, category):
        """
        category - list (str) - tournament category e.g MS - Mens Singles
        """
        self.df = self.df[self.df['event_title'].isin(category)]
        df_unique = pd.DataFrame()
        for v in ['losing_team_p1', 'winning_team_p1']:
            # Get unique players available from 2019 season
            df_tmp = self.df[[f'{v}_tsid', v]].copy(deep=True)
            df_tmp.drop_duplicates(subset=[f'{v}_tsid'], inplace=True)
            df_tmp.columns = ['tsid', 'name']
            df_unique = pd.concat([df_unique, df_tmp])

        df_unique.drop_duplicates(inplace=True)
        df_unique.reset_index(drop=True, inplace=True)
        # Initiate all players with basic 1500 rating
        df_unique['rating'] = 1500
        self.df_unique = df_unique

    def get_all_unique_players(self):
        """
        Find all unique players in results tables
        """
        df_unique = pd.DataFrame()
        for v in ['losing_team_p1', 'winning_team_p1']:
            # Get unique players available from 2019 season
            df_tmp = self.df[[f'{v}_tsid', v]].copy(deep=True)
            df_tmp.drop_duplicates(subset=[f'{v}_tsid'], inplace=True)
            df_tmp.columns = ['tsid', 'name']
            df_unique = pd.concat([df_unique, df_tmp])

        # Add on doubles players
        for v in ['losing_team_p2', 'winning_team_p2']:
            # Get unique players available from 2019 season
            df_tmp = self.df[self.df['Doubles'] == True][[f'{v}_tsid', v]].copy(deep=True)
            df_tmp.drop_duplicates(subset=[f'{v}_tsid'], inplace=True)
            df_tmp.columns = ['tsid', 'name']
            df_unique = pd.concat([df_unique, df_tmp])

        df_unique.drop_duplicates(inplace=True)
        df_unique.reset_index(drop=True, inplace=True)
        # Initiate all players with basic 1500 rating
        df_unique['rating'] = 1500
        self.df_unique = df_unique

    @staticmethod
    def briers_score(predictions, actual):
        return sum([(ft - ot) ** 2 for ft, ot in zip(predictions, actual)]) / len(predictions)

    @staticmethod
    def convert_double_to_single(p1, p2):
        """
        Convert two single players into one player for double comparison

        :param p1: Player object - player 1
        :param p2: Player object - player 2
        :return: Player object - combined p1 and p2
        """
        rating = (p1.rating + p2.rating) / 2
        sd = math.sqrt((p1.sd ** 2) + (p1.sd ** 2))
        name = p1.name + '_' + p2.name
        tsid = str(p1.tsid) + '_' + str(p2.tsid)
        tmp_p = Player(name, tsid, rating=rating, sd=sd)
        return tmp_p

    @staticmethod
    def divide_doubles_points(p1, p2, pts_to_share):
        try:
            p1w_prc = (1 / (1 + math.exp((p1.rating - p2.rating) / p1.sd)))
        except OverflowError:
            print(f"{p1.name} - Rating: {p1.rating:.3f}")
            print(f"{p2.name} - Rating: {p2.rating:.3f}")
            p1w_prc = 0
        p1w_pts = p1w_prc * pts_to_share
        p2w_pts = (1 - p1w_prc) * pts_to_share

        return p1w_pts, p2w_pts

    def singles_match_update(self, row, mov=False, acf=None):
        """
        Provide match prediction and delta to participating players ELO rating's

        :param row: dict - Converted from a single row pd Series of Result Table Schema from PreprocessTourData
        :param mov: bool - Whether to include MOV in rating diff. Default to False
        :param acf: int - Auto-corr-factor in rating diff - typically ~ 1500-2500. Default to None
        :return: result_dict - dict - { prediction: float,
                                    elo: {p1w: {'player_obj': Player Obj, 'pts_chg': pts_change}}
                                    }
        """
        try:
            #Get player tsid, Player objects
            col_headings = [t + p + "_tsid" for t in ['winning_team_', 'losing_team_'] for p in ['p1']]
            tsids = [row[c] for c in col_headings]
            players_obj = [self.player_dict[t] for t in tsids]

            #Calculate ELO rating change and match prediction
            if mov:
                winner_pts_change = self.elo.rating_diff_mov(players_obj[0], players_obj[1], 1, mov=row['pts_diff'], auto_corr_val=acf)
                loser_pts_change = self.elo.rating_diff_mov(players_obj[1], players_obj[0], 0, mov=row['pts_diff'], auto_corr_val=acf)
            else:
                winner_pts_change = self.elo.rating_diff_mov(players_obj[0], players_obj[1], 1, auto_corr_val=acf)
                loser_pts_change = self.elo.rating_diff_mov(players_obj[1], players_obj[0], 0, auto_corr_val=acf)

            pts = [winner_pts_change, loser_pts_change]

            pred = self.elo.expected(players_obj[0], players_obj[1])


            result_dict = {'prediction': pred,
                           'elo': {k: {'player_obj':v, 'pts_chg': v2}
                                   for k, v, v2 in zip(['p1w', 'p1l'], players_obj, pts)}}
            return result_dict

        except Exception as e:
            print(e)
            print(row)
            for ch in ['losing_team_p1_tsid','winning_team_p1_tsid']:
                print(ch[:-5])
                p = self.player_dict[row[ch]]
                print(f'{p.name}: {p.rating}')

    def doubles_match_update(self, row, mov=False, acf=None):
        """
        Provide match prediction and delta to participating players ELO rating's

        :param row: dict - Converted from a single row pd Series of Result Table Schema from PreprocessTourData
        :param mov: bool - Whether to include MOV in rating diff. Default to False
        :param acf: int - Auto-corr-factor in rating diff - typically ~ 1500-2500. Default to None
        :return: result_dict - dict - { prediction: float,
                                    elo: {p1w: {'player_obj': Player Obj, 'pts_chg': pts_change}}
                                    }
        """
        try:
            col_headings = [t + p + "_tsid" for t in ['winning_team_', 'losing_team_'] for p in ['p1', 'p2']]
            tsids = [row[c] for c in col_headings]
            players_obj = [self.player_dict[t] for t in tsids]

            team_w = self.convert_double_to_single(players_obj[0], players_obj[1])
            team_l = self.convert_double_to_single(players_obj[2], players_obj[3])

            #Calculate ELO rating change and match prediction
            if mov:
                winner_pts_change = self.elo.rating_diff_mov(team_w, team_l, 1, mov=row['pts_diff'], auto_corr_val=acf)
                loser_pts_change = self.elo.rating_diff_mov(team_l, team_w, 0, mov=row['pts_diff'], auto_corr_val=acf)
            else:
                winner_pts_change = self.elo.rating_diff_mov(team_w, team_l, 1, auto_corr_val=acf)
                loser_pts_change = self.elo.rating_diff_mov(team_l, team_w, 0, auto_corr_val=acf)

            # Divide points between players - logistic function based on rating and sd
            p1w_pts, p2w_pts = self.divide_doubles_points(players_obj[0], players_obj[1], winner_pts_change)
            p1l_pts, p2l_pts = self.divide_doubles_points(players_obj[2], players_obj[3], loser_pts_change)

            pts = [p1w_pts, p2w_pts, p1l_pts, p2l_pts]
            pred = self.elo.expected(team_w, team_l)

            result_dict = {'prediction': pred,
                           'elo': {k: {'player_obj':v, 'pts_chg': v2}
                                   for k, v, v2 in zip(['p1w', 'p2w', 'p1l', 'p2l'], players_obj, pts)}}
            return result_dict

        except Exception as e:
            print(e)
            print(row)
            for ch in ['losing_team_p1_tsid','losing_team_p2_tsid', 'winning_team_p1_tsid','winning_team_p2_tsid']:
                print(ch[:-5])
                p = self.player_dict[row[ch]]
                print(f'{p.name}: {p.rating}')

    @staticmethod
    def check_min_match_history(result_dict):
        """
        check minimum match history available for all players

        :param result_dict - dict - { 'prediction': float,
                                    elo: {'p1w': {'player_obj': Player Obj, 'pts_chg': pts_change}}
                                    }
        :return: int
        """
        return np.min([len(p['player_obj'].rating_history) for p in result_dict['elo'].values()])

    @staticmethod
    def append_to_eval_cols(eval_cols, result_dict):
        """
        update a eval_cols dict with prior prection, actual, player rating (pr), post pr, min length of rating history
        :param eval_cols: dict -         eval_cols = {'prediction': [],
                                                     'actual': [],
                                                     'p1w_name': [],
                                                     'p2w_name': [],
                                                     'p1l_name': [],
                                                     'p2l_name': [],
                                                     'p1w_rating_prior': [],
                                                     'p2w_rating_prior': [],
                                                     'p1l_rating_prior': [],
                                                     'p2l_rating_prior': [],
                                                     'p1w_rating_post': [],
                                                     'p2w_rating_post': [],
                                                     'p1l_rating_post': [],
                                                     'p2l_rating_post': [],
                                                     'min_rating_hist_len': []
                                                     }
        :param result_dict: - dict - { 'prediction': float,
                                    elo: {'p1w': {'player_obj': Player Obj, 'pts_chg': pts_change}}
                                    }
        :return: eval_cols - dict - updated
        """

        if result_dict:
            eval_cols['prediction'].append(result_dict['prediction'])
            eval_cols['actual'].append(1)

            min_rating_hist_len = 0

            for p in ['p1w', 'p2w', 'p1l', 'p2l']:
                var = result_dict['elo'].get(p)
                #if key in result dict exists, then populate values
                if var:
                    eval_cols[f'{p}_name'].append(var['player_obj'].name)
                    eval_cols[f'{p}_rating_prior'].append(var['player_obj'].rating)
                    eval_cols[f'{p}_rating_post'].append(var['player_obj'].rating + var['pts_chg'])

                    #check rating hist
                    if len(var['player_obj'].rating_history) > min_rating_hist_len:
                        min_rating_hist_len = len(var['player_obj'].rating_history)

                #Otherwise fill with np.nan
                else:
                    eval_cols[f'{p}_name'].append(np.nan)
                    eval_cols[f'{p}_rating_prior'].append(np.nan)
                    eval_cols[f'{p}_rating_post'].append(np.nan)

            eval_cols['min_rating_hist_len'].append(min_rating_hist_len)

        else:
            for k in eval_cols:
                eval_cols[k].append(np.nan)

        return eval_cols

    def check_prediction(self, kfactor=None, sd=None, mov=False, acf=None):

        for row in self.df.itertuples():
            #Add any new players to dict
            self.add_players_to_dict(row, self.df, kfactor=kfactor, sd=sd)

        predictions, actual = [], []

        eval_cols = {'prediction': [],
                     'actual': [],
                     'p1w_name': [],
                     'p2w_name': [],
                     'p1l_name': [],
                     'p2l_name': [],
                     'p1w_rating_prior': [],
                     'p2w_rating_prior': [],
                     'p1l_rating_prior': [],
                     'p2l_rating_prior': [],
                     'p1w_rating_post': [],
                     'p2w_rating_post': [],
                     'p1l_rating_post': [],
                     'p2l_rating_post': [],
                     'min_rating_hist_len': []
                     }

        for row in self.df.itertuples():
            row = row._asdict()
            # Account for Doubles Matches
            if row['Doubles']:
                result_dict = self.doubles_match_update(row, mov=mov, acf=acf)
            else:
                result_dict = self.singles_match_update(row, mov=mov, acf=acf)

            #Update eval cols
            eval_cols = self.append_to_eval_cols(eval_cols, result_dict)

            # If the results could be processed
            if result_dict:
                # update prediction tracker
                if self.check_min_match_history(result_dict) >= self.cold_start_threshold:
                    predictions.append(result_dict['prediction'])
                    actual.append(1)

                # Update player elo ratings and history of elo rating
                for v in result_dict['elo'].values():
                    v['player_obj'].update_rating(v['pts_chg'])

        df_new_cols = pd.DataFrame.from_dict(eval_cols)
        self.df = pd.concat([self.df.reset_index(drop=True), df_new_cols], axis=1)

        return self.briers_score(predictions, actual)
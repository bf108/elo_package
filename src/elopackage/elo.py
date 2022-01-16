import numpy as np
import scipy.stats as stats
import math


class Elo:
    def __init__(self, title):
        self.title = title

    def expected(self, player_a, player_b):
        '''
        Calculated the expected probability of Player A beating Player B

        args:
            player_a - Player object
            player_b - Player object

        returns:
            expected_prob - float - probability of Player A winning (0 -> 1)

        '''
        expected_prob = 1 / (1 + 10 ** ((player_b.rating - player_a.rating) / player_a.sd))
        return expected_prob

    def expected_rv(self, player_a, player_b):
        '''
        Calculated the expected probability of Player A beating Player B

        args:
            player_a - Player object
            player_b - Player object

        returns:
            expected_prob - float - probability of Player A winning (0 -> 1)

        '''
        new_mean = player_a.rating - player_b.rating
        new_std = math.sqrt(player_a.sd ** 2 + player_b.sd ** 2)
        return 1 - stats.norm(loc=new_mean, scale=new_std).cdf(0)

    def rating_diff_mov(self, player_a, player_b, score, mov=None, auto_corr_val=None):
        """
        Calculate the change in rating of Player A, based on score:

        Score: Limited choice of: 1 - Win, 0 - Lose

        args:
            palyer_a - elo object
            palyer_b - elo object
            score - int - 0, 1
            mov - int - margin of victory - Default None
            auto_cor_val - int - factor by which to adjust scores to prevent auto-correlation typically ~2200. Default None

        returns:
            player_a_rate_diff - float - value to adjust rating
        """

        allowed_scores = [0, 1]
        if score not in allowed_scores:
            raise ValueError("Allowable value for score are: 1=Win, 0=Lose")

        if auto_corr_val:
            #Unstable when pa -pb / acf == -1 acf --> inf
            # auto_corr = 1 / (1 + ((player_a.rating - player_b.rating) / auto_corr_val))
            # This is too flat. Even p1 < p2 receives < 0.
            # auto_corr = 1/(1 + math.exp((player_a.rating - player_b.rating)/auto_corr_val))
            # Add factor of 2
            auto_corr = 2 / (1 + math.exp((player_a.rating - player_b.rating) / auto_corr_val))

        else:
            auto_corr = 1

        if mov:
            # if mov < 0:
            #     mov = 0
            # mov_kfactor = np.log(1 + abs(mov) / 2)
            mov_kfactor = np.log(1 + abs(mov))

        else:
            mov_kfactor = 1

        player_a_rate_diff = (score - self.expected(player_a, player_b)) * player_a.kfactor * mov_kfactor * auto_corr
        return player_a_rate_diff


import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import math


class Player:
    def __init__(self, name, tsid, rating=None, kfactor=None, sd=None):
        self.name = name
        self.tsid = tsid

        if rating:
            self.rating = rating
        else:
            self.rating = 1500

        self.rating_history = [self.rating]

        if kfactor:
            self.kfactor = kfactor
        else:
            self.kfactor = 180

        if sd:
            self.sd = sd
        else:
            self.sd = 400

    def update_rating(self, delta):
        """
        Update a players rating with delta and player rating history
        :param delta - float - delta of player's rating:
        :return: none
        """
        self.rating += delta
        self.rating_history.append(self.rating)

    def visualize_competitor(self, p2):
        """
        2D Plot of distribution of both players

        args:
            p2 - Player Object of opposition

        return:
            matplotlib fig object
        """
        plt.rcParams.update({'font.size': 15})
        min_rating = min(self.rating, p2.rating)
        max_rating = max(self.rating, p2.rating)
        min_x = round((min_rating - 4 * self.sd))
        max_x = round((max_rating + 4 * self.sd))

        x = np.arange(min_x, max_x, 1)
        fig, ax = plt.subplots()
        ax.plot(x, stats.norm(self.rating, self.sd).pdf(x), label=f'{self.name}\nTSID: {int(self.tsid)}\nRating: {int(self.rating)}')
        ax.plot(x, stats.norm(p2.rating, p2.sd).pdf(x), label=f'{p2.name}\nTSID: {int(p2.tsid)}\nRating: {int(p2.rating)}')
        ax.set_title('Comparison of Players Rating')
        ax.set_xlabel('Rating')
        ax.set_ylabel('Probability Density')
        plt.legend(bbox_to_anchor=(-0.1, -0.2), loc="upper left", ncol=2)
        plt.tight_layout()
        plt.show()

        return fig

    def visualize_prob_winning(self, p2):
        """
        2D Plot showing distribution and probability of player beating p2

        args:
            p2 - Player Object of opposition

        return:
            matplotlib fig object
        """
        plt.rcParams.update({'font.size': 15})
        new_mean = self.rating - p2.rating
        new_std = math.sqrt(self.sd ** 2 + p2.sd ** 2)
        p_p1_winning = 1 - stats.norm(loc=new_mean, scale=new_std).cdf(0)

        x = np.arange(round(new_mean - 4 * new_std), round(new_mean + 4 * new_std), 1)

        fig, ax = plt.subplots()
        ax.plot(x, stats.norm(new_mean, new_std).pdf(x), label=f'P({self.name} beating {p2.name}) = {p_p1_winning:.3f}')

        x_fill_max = np.arange(0, round(new_mean + 4 * new_std))
        y1 = stats.norm(loc=new_mean, scale=new_std).pdf(x_fill_max)
        ax.fill_between(x_fill_max, y1, alpha=0.3)
        plt.legend(bbox_to_anchor=(0, 1.04), loc="lower left")
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        plt.tight_layout()
        plt.show()

        return fig

    def visualize_rating_hist(self):
        """
        2D Plot showing player ELO rating changes overtime

        args:None
        return: matplotlib fig object
        """
        plt.rcParams.update({'font.size': 15})
        fig, ax = plt.subplots()
        ax.plot(np.arange(len(self.rating_history)), self.rating_history, label=f'{self.name} ELO Rating History')
        ax.scatter(np.arange(len(self.rating_history)), self.rating_history)
        plt.legend(bbox_to_anchor=(0, 1.04), loc="lower left")
        ax.set_xlabel('Number of Games Played')
        ax.set_ylabel('Player Rating');
        plt.tight_layout()
        plt.show()

        return fig

    def combine(self, p2):
        """
        Returns a new player object which is a combination of existing and p2

        This assumes skill of players is independant - No correlation between players.

        p2 - Player object
        """
        rating_combined = (self.rating + p2.rating) / 2
        sd_combined = math.sqrt(self.sd ** 2 + p2.sd ** 2)
        name_combined = self.name + "_" + p2.name
        tsid_combined = self.tsid + "_" + p2.tsid

        return Player(name_combined, tsid_combined, rating=rating_combined, sd=sd_combined)

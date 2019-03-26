import math
import numpy
"""
Source: http://www.glicko.net/glicko/glicko2.pdf
"""



class Glicko2(object):

    def __init__(self, team_name, games, exclude_=None):
        self.team = None

        if exclude_ is None or exclude_.lower() != "home":

            home_games = [game for game in games if (game.home_team.abbr == team_name.lower() or
                                                     game.home_team.name == team_name.lower())]
            home_opponents = [Glicko2._initialize_rank(game.away_team) for game in home_games]
            if self.team is None:
                self.team = Glicko2._initialize_rank(home_games[0].home_team)

        else:
            home_games = []
            home_opponents = []

        if exclude_ is None or exclude_.lower() != "away":
            away_games = [game for game in games if (game.away_team.abbr == team_name.lower() or
                                                     game.away_team.name.lower() == team_name.lower())]
            away_opponents = [Glicko2._initialize_rank(game.home_team) for game in away_games]
            if self.team is None:
                self.team = Glicko2._initialize_rank(away_games[0].away_team)
        else:
            away_games = []
            away_opponents = []

        self.team_games = home_games + away_games
        self.opponents = home_opponents + away_opponents


    @staticmethod
    def _initialize_rank(team):
        """
        Formatted in following order
        (old_rank, old_rank_dev, old_volatility,
        new_rank, new_rank_dev, new_volatility,
        scaled_rank [mu], scaled_rank_dev [phi])
        :param team:
        :return:
        """

        if team.glicko2 is None:
            team.glicko2 = {"old_rank": 0, "old_rd": 0,
                            "old_volty": 0, "rank": 1500,
                            "rd": 350, "volty": .06,
                            "mu": 0, "phi": 0}
        else:
            pass
        return Glicko2.scale(team)

    @staticmethod
    def scale(team):
        # Proxy for mu
        team.glicko2['mu'] = team.glicko2['rank'] - 1500 / 173.7178
        # Proxy for phi
        team.glicko2['phi'] = team.glicko2['rd'] / 173.7178
        return team


    @staticmethod
    def g(phi):
        return (1 / math.sqrt((1 + 3*(phi**2))/(math.pi**2)))

    @staticmethod
    def E(mu, mu_j, g_j):
        if mu == mu_j:
            return 1/2
        else:
            return 1 / (1 + math.exp(((-1 * g_j) * (mu - mu_j))))

    @staticmethod
    def variance_single(phi_j, mu_j, mu):
        g_j = g(phi_j)
        E_j = Glicko2.E(mu, mu_j, g_j)
        return g_j**2 * E_j * (1-E_j)

    @staticmethod
    def delta_single(phi_j, mu_j, mu, expected_team_outcome):
        """
        the estimated improvement in rating by comparing the
        pre-period rating to the performance rating based only
        on game outcomes.

        :param mu:
        :param opponents:
        :param expected_outcome:
        :return:
        """

        g_j = Glicko2.g(phi_j)
        E_j = Glicko2.E(mu, mu_j, g_j)

        d = g_j * (expected_team_outcome - E_j)
        return d

    @staticmethod
    def volatility_func(x, a, t, delta, phi, v):
        f1_num = math.exp(x) * ((delta ** 2) - (phi ** 2) - v - math.exp(x))
        f1_denom = (2 * ((phi ** 2) + v + math.exp(x))) ** 2

        f2 = (x - a)/(t**2)

        f1  = f1_num/f1_denom

        return f1 - f2

    def variance(self):
        v = 0
        for opp in self.opponents:
            mu_j, phi_j = opp.glicko2["mu"], opp.glicko2["phi"]
            mu = self.team.glicko2["mu"]
            v += Glicko2.variance_single(phi_j, mu_j, mu)
        return 1 / v

    def delta(self):
        dx = sum([Glicko2.delta_single(self.opponents[o].glicko2[4], self.opponents[o].glicko2[3], self.team.glicko2[3], self.team_games[o].expected_outcome(self.team.abbr)) for o in range(len(self.opponents))])
        return self.variance() * dx

    def volatility(self, x=None, tau=.7, epsilon=.000001):
        k = 1
        a = math.log(math.exp(self.team.glicko2["old_volty"]**2))
        delt = self.delta()
        phi = self.team.glicko2["phi"]
        v = self.variance()

        if (delt**2) > ((phi**2) + v):
            b = math.log(math.exp((delt**2) - (phi**2) - v))
        else:
            vol = Glicko2.volatility_func(x=(a-(k*tau)), a=a, t=tau, delta=delt, phi=phi, v=v)
            if vol < 0:
                k += 1
                self.volatility(x=a - k * tau)
            else:
                b = a - k * tau

        f_a = Glicko2.volatility_func(a, a, tau, delt, phi, v)
        f_b = Glicko2.volatility_func(b, a, tau, delt, phi, v)

        while abs((b - a)) > epsilon:
            c = (a + (a - b) * f_a) / (f_b - f_a)
            f_c = Glicko2.volatility_func(c, a, tau, delt, phi, v)

            if f_c * f_b < 0:
                a = b
                f_a = f_b
            else:
                f_a = f_a/2
            b = c
            f_b = f_c

        else:
            return math.exp(a/2)

    def updated_rd(self):
        phi = self.team.glicko2[4]
        volty = self.volatility()
        self.team.glicko2.update({"old_volty": volty})
        self.team.glicko2['volty'] = volty
        return math.sqrt(phi**2 + volty**2)

    def adjust_ratings(self):
        v = self.variance()
        mu = self.team.glicko2[3]
        phi_prime = 1 / math.sqrt((1/(self.updated_rd()**2)) + (1/v))

        mu_prime = mu + (phi_prime**2)*sum([Glicko2.delta_single(phi_j=self.opponents[o].glicko2[4],
                                                                 mu_j=self.opponents[o].glicko2[3], mu=mu,
                                                                 expected_team_outcome=self.team_games[o].expected_outcome(self.team.abbr))
                                            for o in range(len(self.opponents))])
        self.team.glicko2.update({"old_rank": self.team.glicko2['rank'],
                                  "old_rd": self.team.glicko2['rd'],
                                  "old_volty": self.team.glicko2['volty']})

        self.team.glicko2["rank"] = (173.7178 * mu_prime) + 1500
        self.team.glicko2["rd"] = (173.7178 * phi_prime)

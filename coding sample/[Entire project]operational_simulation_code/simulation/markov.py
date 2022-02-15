import simpy
import random

from .util import get_month

# case A: Apr. to Oct. (p_qq = 0.99, p_ss = 0.70), Jan. to Mar. & Nov. to Dec. (p_qq = 0.98, p_ss = 0.75)
# case B: Apr. to Oct. (p_qq = 0.98, p_ss = 0.75), Jan. to Mar. & Nov. to Dec. (p_qq = 0.95, p_ss = 0.90)

# case A
# Apr. to Oct.
p_qq_1 = 0.99
p_ss_1 = 0.60
# Jan. to Mar. & Nov. to Dec.
p_qq_2 = 0.95
p_ss_2 = 0.65

# # case B
# # Apr. to Oct.
# p_qq_1 = 0.98
# p_ss_1 = 0.65
# # Jan. to Mar. & Nov. to Dec.
# p_qq_2 = 0.90
# p_ss_2 = 0.70


class OceanMarkovChainSimulation(object):
    """
    simulates wave state using a markov chain method
    Ref: "On the Duration of Calm and Harsh Wave States in the Sea around Japan" by Ryota Wada & Masahiko Ozaki
    """

    def __init__(self, env: simpy.Environment):
        self.is_quiet = True
        self.env = env
        self.p_qq = 0  # q = "quiet", s = "stormy"
        self.p_qs = 0
        self.p_ss = 0
        self.p_sq = 0

    def check_sea_is_stable(self) -> bool:
        rand = random.random()
        # define transition probability for each month
        if get_month(self.env.now) == 1:
            self.p_qq, self.p_qs, self.p_ss, self.p_sq = p_qq_2, 1 - p_qq_2, p_ss_2, 1 - p_ss_2
        elif get_month(self.env.now) == 2:
            self.p_qq, self.p_qs, self.p_ss, self.p_sq = p_qq_2, 1 - p_qq_2, p_ss_2, 1 - p_ss_2
        elif get_month(self.env.now) == 3:
            self.p_qq, self.p_qs, self.p_ss, self.p_sq = p_qq_2, 1 - p_qq_2, p_ss_2, 1 - p_ss_2
        elif get_month(self.env.now) == 4:
            self.p_qq, self.p_qs, self.p_ss, self.p_sq = p_qq_1, 1 - p_qq_1, p_ss_1, 1 - p_ss_1
        elif get_month(self.env.now) == 5:
            self.p_qq, self.p_qs, self.p_ss, self.p_sq = p_qq_1, 1 - p_qq_1, p_ss_1, 1 - p_ss_1
        elif get_month(self.env.now) == 6:
            self.p_qq, self.p_qs, self.p_ss, self.p_sq = p_qq_1, 1 - p_qq_1, p_ss_1, 1 - p_ss_1
        elif get_month(self.env.now) == 7:
            self.p_qq, self.p_qs, self.p_ss, self.p_sq = p_qq_1, 1 - p_qq_1, p_ss_1, 1 - p_ss_1
        elif get_month(self.env.now) == 8:
            self.p_qq, self.p_qs, self.p_ss, self.p_sq = p_qq_1, 1 - p_qq_1, p_ss_1, 1 - p_ss_1
        elif get_month(self.env.now) == 9:
            self.p_qq, self.p_qs, self.p_ss, self.p_sq = p_qq_1, 1 - p_qq_1, p_ss_1, 1 - p_ss_1
        elif get_month(self.env.now) == 10:
            self.p_qq, self.p_qs, self.p_ss, self.p_sq = p_qq_1, 1 - p_qq_1, p_ss_1, 1 - p_ss_1
        elif get_month(self.env.now) == 11:
            self.p_qq, self.p_qs, self.p_ss, self.p_sq = p_qq_2, 1 - p_qq_2, p_ss_2, 1 - p_ss_2
        elif get_month(self.env.now) == 12:
            self.p_qq, self.p_qs, self.p_ss, self.p_sq = p_qq_2, 1 - p_qq_2, p_ss_2, 1 - p_ss_2

        if self.is_quiet:
            if rand <= self.p_qs:
                self.is_quiet = False
        else:
            if rand <= self.p_sq:
                self.is_quiet = True

        return self.is_quiet

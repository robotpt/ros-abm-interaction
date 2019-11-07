import numpy as np
import queue
from robotpt_common_utils import lists
from hmmlearn import hmm


class Bkt:

    def __init__(self, pL0, pT, pS, pG):

        self._pL = pL0
        self._pT = pT
        self._pS = pS
        self._pG = pG

    def _get_model(self):
        model = hmm.MultinomialHMM(n_components=len(self._priors))
        model.startprob_ = self._priors
        model.transmat_ = self._transitions_matrix
        model.emissionprob_ = self._observations_matrix
        return model

    def sample(self, n: int):
        model = self._get_model()
        X, _ = model.sample(n)
        return Bkt._hmmlearn_number_array_to_bool_list(X)

    @staticmethod
    def _hmmlearn_number_array_to_bool_list(nums, value_for_true=1):
        nums = lists.make_sure_is_iterable(nums)
        return [n[0] == value_for_true for n in nums]

    def fit(self, X, lengths=None):
        model = self._get_model()
        X = Bkt._bool_list_to_hmmlearn_number_array(X)
        model.fit(X, lengths)

        pL_ = model.startprob_[0]
        pT_ = model.transmat_[1][0]
        pS_ = model.transmat_[0][1]
        pG_ = model.transmat_[1][0]

        return Bkt(pL_, pT_, pS_, pG_)

    @staticmethod
    def _bool_list_to_hmmlearn_number_array(bools, value_if_true=1, value_if_false=0):
        bools = lists.make_sure_is_iterable(bools)
        return [[value_if_true] if b else [value_if_false] for b in bools]

    def update(self, observations):
        observations = lists.make_sure_is_iterable(observations)
        for o in observations:
            if o is True:
                pL_ = (self._pL*(1-self._pS)) / (self._pL*(1-self._pS) + (1-self._pL)*self._pG)
            else:
                pL_ = (self._pL*self._pS) / (self._pL*self._pS + (1-self._pL)*(1-self._pG))
            self._pL = pL_
        return Bkt(pL_, self._pT, self._pS, self._pG)

    def get_automaticity(self):
        return self._pL

    @property
    def _pL(self):
        return self._pL_

    @_pL.setter
    def _pL(self, value, epsilon=5e-2):
        """
        Make sure that _pL_ is never set to exactly 1 or 0,
        which would make the BKT degenerate
        """

        if value >= 1:
            pL_ = 1-epsilon
        elif value <= 0:
            pL_ = 0+epsilon
        else:
            pL_ = value
        self._pL_ = pL_

    @property
    def _priors(self):
        return np.array([self._pL,
                         1-self._pL])

    @property
    def _transitions_matrix(self):
        return np.array([[1, 0],
                         [self._pT, 1-self._pT]])

    @property
    def _observations_matrix(self):
        return np.array([[1-self._pS, self._pS],
                         [self._pG, 1-self._pG]])


if __name__ == '__main__':

    np.random.seed(42)

    pL0_ = 0.0
    pT_ = 0.02
    pS_ = 0.3
    pG_ = 0.5

    bkt = Bkt(pL0_, pT_, pS_, pG_)

    for update in [True, True, [True, False]]*round(42/4):
        bkt = bkt.update(update)
        print(bkt.get_automaticity())

    print("====================")
    print("BEFORE FIT")
    print("====================")
    print("The transmission matrix probability is: ")
    print(bkt._transitions_matrix)
    print("--------------------")
    print("The emission probability matrix is: ")
    print(bkt._observations_matrix)
    print("--------------------")
    print("The start probability matrix is: ")
    print(bkt._priors)
    print("--------------------")

    X = bkt.sample(100)
    bkt = bkt.fit(X)
    print("====================")
    print("AFTER FIT")
    print("====================")
    print("The transmission matrix probability is: ")
    print(bkt._transitions_matrix)
    print("--------------------")
    print("The emission probability matrix is: ")
    print(bkt._observations_matrix)
    print("--------------------")
    print("The start probability matrix is: ")
    print(bkt._priors)
    print("--------------------")

q = queue.Queue(maxsize=100)

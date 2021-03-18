from attrdict import AttrDict
from db.model import Basic
from db.factory import BasicFactory, ScoreFactory
from scipy.signal import argrelextrema
from sklearn.neighbors import KernelDensity
from util.config import config
import numpy as np


class Cluster:
    def __init__(self):
        self._nvm = config.score.num_votes
        self._rtm = config.score.runtime
        self._ym = config.score.year
        self._ttm = config.score.title_type

    def _scoring(self):
        """
        Calculate score for the movies

        :return: scores and title ids
        :rtype: AttrDict
        """
        sf = ScoreFactory()

        # get data which contains features
        records = sf.get_all()

        scores = []
        title_ids = []

        for record in records:
            vote_score = self._nvm * record.num_votes
            runtime_score = self._rtm * record.runtime
            year_score = self._ym * record.start_year
            tt_score = self._ttm * record.title_type

            # find total score
            score = vote_score + runtime_score + year_score + tt_score
            scores.append(score)

            # title ids
            title_ids.append(record.title_id)

        result = AttrDict()
        result.title_ids = title_ids
        result.scores = scores

        return result

    def clustering(self):
        """
        Find clusters for the movies and save to database
        """
        result = self._scoring()

        # kernel density estimation
        scores = np.array(result.scores).reshape(-1, 1)
        kde = KernelDensity(kernel='gaussian', bandwidth=3).fit(scores)

        # find cluster min-max points
        s = np.linspace(650, 18000)
        e = kde.score_samples(s.reshape(-1, 1))
        mi, ma = argrelextrema(e, np.less)[0], argrelextrema(e, np.greater)[0]

        # concat min-max points
        points = np.concatenate((s[mi], s[ma]), axis=0)
        buckets = []

        for point in points:
            buckets.append(point)

        buckets = np.array(buckets)
        buckets.sort()

        # assign clusters
        clusters = buckets.searchsorted(scores)

        bf = BasicFactory()

        # update basic objects
        instances = []
        for title_id, cluster in zip(result.title_ids, clusters):
            basic = Basic()
            basic.title_id = title_id
            basic.cluster = cluster.item(0)

            instances.append(basic)

        bf.save_all(instances)

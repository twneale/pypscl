import os
import json
from collections import defaultdict

from pandas import DataFrame
from rpy2.robjects.packages import importr
import pymongo

from pscl.rollcall import Rollcall
from pscl.ideal import ideal


pscl = importr('pscl')


if __name__ == '__main__':

    import sys
    state = sys.argv[1]
    session = sys.argv[2]
    chamber = sys.argv[3]

    MISSING = 3

    client = pymongo.MongoClient()
    db = client.fiftystates

    spec = dict(state=state, session=session, chamber=chamber)
    # spec = dict(state='ny', session='2013-2014', chamber='upper')
    chamber = spec['chamber']
    bill_ids = db.bills.find(spec).distinct('_id')
    votes = db.votes.find(
        {'bill_id': {'$in': bill_ids},
         'chamber': chamber})#.limit(50)

    votedata = defaultdict(dict)
    vote_vals = dict(yes_votes=1, no_votes=2, other_votes=3)
    leg_ids = set()

    for vote in votes:
        for k in 'yes_votes, no_votes, other_votes'.split(', '):
            for voter in vote[k]:
                leg_id = voter['leg_id']
                if leg_id is None:
                    continue
                leg_ids.add(leg_id)
                votedata[vote['_id']][leg_id] = vote_vals[k]
    leg_ids = list(filter(None, leg_ids))

    for vote_id, votes in votedata.items():
        votedata[vote_id] = map(lambda leg_id: votes.get(leg_id, MISSING), leg_ids)

    # Convert the dict into a pandas DataFrame.
    dataframe = DataFrame(votedata, index=leg_ids)

    # Create a rollcall object similar to pscl's.
    rollcall = Rollcall.from_dataframe(dataframe,
        yea=[1],
        nay=[2],
        missing=[3],
        not_in_legis=0.0,
        legis_names=leg_ids)

    xbar = ideal(rollcall).xbar
    legs = db.legislators.find(dict(state=state))
    legs = {leg['_id']: leg for leg in legs}

    fn = '~/sunlight/openstates/experimental/birdy/data/%s-xbar.json' % '.'.join(sys.argv[1:])
    with open(os.path.expanduser(fn), 'w') as f:
        json.dump(xbar, f)

    sys.exit(1)
    import pdb; pdb.set_trace()
    # for k, v in xbar.items():
    #     print k, v, legs[k]['full_name'], legs[k]['party']

    positive = [v for v in xbar.values() if v > 0]
    negative = [v for v in xbar.values() if v <= 0]

    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.stats import gaussian_kde

    # plt.hist(negative, 50, normed=1, facecolor='b', alpha=0.75, histtype='stepfilled')
    # plt.hist(positive, 50, normed=1, facecolor='r', alpha=0.75, histtype='stepfilled')

    neg_density = gaussian_kde(negative)
    neg_xs = np.linspace(min(negative), max(positive), 200)
    neg_density.covariance_factor = lambda: .25
    neg_density._compute_covariance()

    pos_density = gaussian_kde(positive)
    pos_xs = np.linspace(min(negative), max(positive), 200)
    pos_density.covariance_factor = lambda: .25
    pos_density._compute_covariance()

    # x = plt.plot(pos_xs, pos_density(pos_xs), 'r')

    x = plt.plot(pos_xs, pos_density(pos_xs), 'r', neg_xs, neg_density(neg_xs), 'b')
    y = plt.fill_between(pos_xs, pos_density(pos_xs), 0, color='r')
    z = plt.fill_between(neg_xs, neg_density(neg_xs), 0, color='b')
    # y = plt.fill(pos_xs, pos_density(pos_xs), 'r', neg_xs, neg_density(neg_xs), 'b')

    plt.grid(True)
    plt.show()

    import pdb; pdb.set_trace()

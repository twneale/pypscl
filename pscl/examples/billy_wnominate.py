from collections import defaultdict

from pandas import DataFrame
from rpy2.robjects.packages import importr

from billy.core import db
from pscl import Rollcall, wnominate


pscl = importr('pscl')


if __name__ == '__main__':

    import sys
    state = sys.argv[1]
    session = sys.argv[2]
    chamber = sys.argv[3]

    MISSING = 3

    spec = dict(state=state, session=session, chamber=chamber)
    # spec = dict(state=state, session='2013-2014', chamber=chamber)
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

    wn = wnominate(rollcall, polarity=['NYL000161', 'NYL000134'])

    import pdb; pdb.set_trace()

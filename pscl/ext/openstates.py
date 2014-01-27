import logging
from collections import defaultdict

from pscl import Rollcall
from pandas import DataFrame


class RollcallBuilder(object):
    '''Provides an easy(ish) way to build a rollcall object from
    the Open States API.
    '''
    def __init__(self, valid_ids, YES=1, NO=2, OTHER=3, NA=9):
        self.votedata = defaultdict(dict)
        self.YES = float(YES)
        self.NO = float(NO)
        self.OTHER = float(OTHER)
        self.NA = float(NA)
        self.vote_vals = dict(
            yes_votes=self.YES,
            no_votes=self.NO,
            other_votes=self.OTHER)
        self.valid_ids = valid_ids
        self.leg_ids = set()

    def add_vote(self, vote):
        vote_keys = 'yes_votes, no_votes, other_votes'.split(', ')
        valid_ids = self.valid_ids
        vote_vals = self.vote_vals
        leg_ids = self.leg_ids
        for k in vote_keys:
            for voter in vote[k]:
                leg_id = voter['leg_id']
                if leg_id is None:
                    continue
                if leg_id not in valid_ids:
                    continue
                leg_ids.add(leg_id)
                self.votedata[vote['id']][leg_id] = vote_vals[k]

    def get_rollcall(self):
        # Convert the dict into a pandas DataFrame.
        dataframe = DataFrame(self.votedata, index=self.leg_ids)
        dataframe.fillna(value=self.NA)

        # Create a rollcall object similar to pscl's.
        rollcall = Rollcall.from_dataframe(dataframe,
            yea=[self.YES],
            nay=[self.NO],
            missing=[self.OTHER],
            not_in_legis=0.0,
            legis_names=tuple(self.leg_ids))

        return rollcall


if __name__ == '__main__':
    from sunlight import openstates, cache
    cache.enable('mongo')
    cache.logger.setLevel(10)

    spec = dict(state='al', chamber='lower', search_window='term:2011-2014')
    valid_ids = [leg['id'] for leg in openstates.legislators(**spec)]
    builder = RollcallBuilder(valid_ids)
    bills = openstates.bills(**spec)
    for bill in bills:
        bill = openstates.bill(bill['id'])
        for vote in bill['votes']:
            if vote['chamber'] != bill['chamber']:
                continue
            builder.add_vote(vote)

    rollcall = builder.get_rollcall()
    import pdb; pdb.set_trace()

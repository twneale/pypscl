'''Parse voteview.com .ord files.
'''
from itertools import izip
from operator import itemgetter
from collections import defaultdict
from StringIO import StringIO
from collections import namedtuple

from rpy2.robjects.packages import importr

from pandas import DataFrame
from pandas.rpy import common as rpy_common

from pscl.utils import Cached
from pscl.rollcall import RollcallBuilder


rpscl = importr('pscl')


VoterData = namedtuple('VoterData', (
    'congress_number',
    'icpsr_id',
    'state_code',
    'cong_district',
    'state_name',
    'party_code',
    'occupancy',
    'attained_office',
    'name',
    'votes',
    ))


class OrdFile(object):
    '''Parse the contents of a voteview.com congressional vote .ord file
    into a stream of namedtuples. The files are fixed-width ascii.
    '''
    def __init__(self, fp):
        self.fp = fp

    def __iter__(self):
        self.fp.seek(0)
        while True:
            yield next(self)

    def next(self):
        line = next(self.fp)
        bf = StringIO(line)
        data = VoterData(
            congress_number=bf.read(3).strip(),
            icpsr_id=bf.read(5).strip(),
            state_code=bf.read(2).strip(),
            cong_district=bf.read(2).strip(),
            state_name=bf.read(8).strip(),
            party_code=bf.read(3).strip(),
            occupancy=bf.read(1).strip(),
            attained_office=bf.read(1).strip(),
            name=bf.read(11).strip(),
            votes=list(bf.read().strip()))
        return data

    def as_rollcall(self):
        x =  '''{u'vote_id': u'AKV00000303',
         u'no_votes': [],
         u'other_votes': [{u'leg_id': u'AKL000004', u'name': u'Coghill'},
                          {u'leg_id': u'AKL000016', u'name': u'Stedman'}],
         u'yes_votes': [{u'leg_id': u'AKL000005', u'name': u'Davis'},
                        {u'leg_id': u'AKL000018', u'name': u'Wagoner'},
                        {u'leg_id': u'AKL000019', u'name': u'Wielechowski'}]}

        '''

        class Votes(dict):
            def __missing__(self, vote_id):
                data = dict(
                    vote_id=vote_id,
                    no_votes=[],
                    yes_votes=[],
                    other_votes=[])
                self[vote_id] = data
                return data

        votes = list(self)
        votes = map(itemgetter(-1), votes)
        votes = dict(enumerate(izip(*votes)))
        vote_ids = list(votes)

        names = [x.name for x in self]

        dataframe = DataFrame(votes, index=names)
        matrix = rpy_common.convert_to_r_matrix(dataframe)
        import nose.tools;nose.tools.set_trace()

        votes = Votes()
        for voterdata in self:
            for i, vote in enumerate(voterdata.votes):
                i = str(i)
                if vote == '1':
                    key = 'yes_votes'
                elif vote == '6':
                    key = 'no_votes'
                elif vote == '9':
                    key = 'other_votes'

                votes[i][key].append(
                    dict(leg_id=voterdata.icpsr_id, name=voterdata.name))

        builder = RollcallBuilder()
        for vote_id, vote in votes.items():
            builder.add_vote(vote)

        return builder.build()

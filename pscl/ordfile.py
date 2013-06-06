'''Parse voteview.com .ord files.
'''
from StringIO import StringIO
from collections import namedtuple, defaultdict

from pandas import DataFrame, Series
from pandas.rpy import common as rpy_common

from pscl.rollcall import Rollcall


VoterData = namedtuple('VoterData', (
    'congress_number',

    # aka "icpsrLegis"
    'icpsr_id',

    # aka "icpsrState"
    'state_code',

    # aka "cd"
    'cong_district',

    # aka "state"
    'state_name',

    # aka "party"
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
            votes=map(float, list(bf.read().strip())))
        return data

    def as_rollcall(self):

        # Convert the ord file into a mapping of vote_ids to lists of
        # vote values, where list index position corresponds to voter_id.
        votes = []
        names = []
        for vote in self:
            votes.append(vote.votes)
            names.append(vote.name)
        votes_dict = dict(enumerate(zip(*votes)))

        # Convert the mapping into a pandas DataFrame.
        dataframe = DataFrame(votes_dict, index=names)

        # Also create the legis.data DataFrame.
        # rows = []
        # for vote in self:
        #     rows.append(dict(
        #         state=vote.state_code,
        #         icpsrState=vote.state_code,
        #         cd=vote.cong_district,
        #         icpsrLegis=vote.icpsr_id,
        #         party=vote.party_code
        #         ))

        rowdata = defaultdict(list)
        for vote in self:
            colnames = ('state_name', 'state_code', 'cong_district',
                        'icpsr_id', 'party_code')
            for colname in colnames:
                rowdata[colname].append(getattr(vote, colname))

        rows = {}
        for k, v in rowdata.items():
            rows[k] = Series(v, index=names)
        legis_data = DataFrame(rows)

        # Create a rollcall object similar to pscl's.
        rollcall = Rollcall.from_dataframe(dataframe,
            yea=[1.0, 2.0, 3.0],
            nay=[4.0, 5.0, 6.0],
            missing=[7.0, 8.0, 9.0],
            not_in_legis=0.0,
            legis_names=names)

        import nose.tools;nose.tools.set_trace()
        return rollcall

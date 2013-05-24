'''Parse voteview.com .ord files.
'''
from StringIO import StringIO
from collections import namedtuple

from utils import Cached


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

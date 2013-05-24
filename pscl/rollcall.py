import json
import collections

import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

from .base import Field, Builder, Wrapper
from .utils import Cached


pscl = importr('pscl')
rjsonio = importr('RJSONIO')


class Rollcall(Wrapper):

    def drop_unanimous(self, lop=0):
        self.obj = pscl.dropUnanimous(self.obj, lop=0)
        return self

    def drop_rollcall(self, lop=0):
        self.obj = pscl.dropRollCall(self.obj, dropList)
        return self

    def summary(self):
        return pscl.summary_rollcall(self.obj)


class RollcallBuilder(Builder):
    '''A python wrapper around the R pscl pacakge's rollcall object.
    '''
    r_type = pscl.rollcall
    wrapper = Rollcall

    yea = Field(name='yea', default=1)
    nay = Field(name='nay', default=2)
    missing = Field(name='missing', default=None)
    not_in_legis = Field(name='notInLegis', default=9)
    legis_names = Field(name='legis.names', default=None)
    vote_names = Field(name='vote.names', default=None)
    legis_data = Field(name='legis.data', default=None)
    vote_data = Field(name='vote.data', default=None)
    desc = Field(name='desc', default=None)
    source = Field(name='source', default=None)

    def __init__(self, *args, **kwargs):
        super(RollcallBuilder, self).__init__(*args, **kwargs)
        self._data = collections.defaultdict(dict)

    @Cached
    def _unflatten(self):
        '''R-jutsu contributed by the incomparable Adam Hyland
        [https://github.com/Protonk].
        '''
        rcode = '''
            unflatten <- function(json) {
              legis.list <- fromJSON(json)
              legis.names <- unique(names(unlist(unname(legis.list))))
              prefill <- vector("numeric", length = length(legis.names))
              sortStretch <- function(orig) {
                prefill[] <- NA
                prefill[match(names(orig), legis.names)] <- orig
                return(prefill)
              }
              square <- lapply(legis.list, sortStretch)
              out.mat <- t(do.call(rbind, square))
              rownames(out.mat) <- legis.names
              return(out.mat)
            }
            '''
        return robjects.r(rcode)

    @Cached
    def data(self):
        '''Build the rollcall data and return is a nested dict.
        '''
        self.add_votes()
        return dict(self._data)

    def json(self):
        return json.dumps(self.data)

    def robject(self):
        '''Return this instance's internal rollcall data structure as a
        pscl.rollcall object.
        '''
        rdata = self._unflatten(self.json())
        r_object = self.r_type(rdata, **self.r_kwargs())
        if hasattr(self, 'wrapper'):
            r_object = self.wrapper(r_object)
        return r_object

    def add_votes(self):
        '''Override this function to access a data source and call
        self.add_vote for each rollcall vote in the dataset.
        '''

    def add_vote(self, vote):
        '''Add a single vote to this instance's internal rollcall
        datastructure. Expects an object like this:

        {u'vote_id': u'AKV00000303',
         u'no_votes': [],
         u'other_votes': [{u'leg_id': u'AKL000004', u'name': u'Coghill'},
                          {u'leg_id': u'AKL000016', u'name': u'Stedman'}],
         u'yes_votes': [{u'leg_id': u'AKL000005', u'name': u'Davis'},
                        {u'leg_id': u'AKL000018', u'name': u'Wagoner'},
                        {u'leg_id': u'AKL000019', u'name': u'Wielechowski'}]}

        '''
        data = self._data
        vote_id = vote['vote_id']
        keyvals = (('yes_votes', self.yea),
                   ('no_votes', self.nay))
        for key, val in keyvals:
            votes = vote[key]
            for v in votes:
                leg_id = v['leg_id']
                if leg_id is None:
                    continue
                data[leg_id][vote_id] = val

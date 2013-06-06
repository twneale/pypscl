import json
import collections
import operator

from pandas import DataFrame
from pandas.rpy import common as rpy_common

import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

from .base import Field, Translator, Wrapper
from .accessors import LastVectorItemAccessor, VectorAccessor
from .utils import Cached


pscl = importr('pscl')


class RollcallSummary(Wrapper):

    all_votes = VectorAccessor('allVotes')
    n = LastVectorItemAccessor('n')
    m = LastVectorItemAccessor('m')

    eq_attrs = ('m', 'n', 'codes', 'all_votes')

    @property
    def codes(self):
        '''Return a mapping of vote values like "yea" or "nay" to
        the "codes" (in the docs, integers) that represent them
        in the underlying Rollcall object.
        '''
        items = []
        for yes_no_other, value_list in self['codes'].iteritems():
            items.append((yes_no_other, tuple(value_list)))
        return dict(items)


class Rollcall(Wrapper):

    # Wrapped R functions ---------------------------------------------------
    def drop_unanimous(self, lop=0):
        self.obj = pscl.dropUnanimous(self.obj, lop=0)
        return self

    def summary(self):
        return RollcallSummary(pscl.summary_rollcall(self.obj))

    # Accessors ---------------------------------------------------------------
    n = LastVectorItemAccessor('n')
    m = LastVectorItemAccessor('m')
    all_votes = VectorAccessor('votes')

    eq_attrs = ('m', 'n', 'codes', 'all_votes')

    @property
    def codes(self):
        '''Return a mapping of vote values like "yea" or "nay" to
        the "codes" (in the docs, integers) that represent them
        in the underlying Rollcall object.
        '''
        items = []
        for yes_no_other, value_list in self['codes'].iteritems():
            items.append((yes_no_other, tuple(value_list)))
        return dict(items)

    @classmethod
    def from_matrix(cls, r_matrix, **kwargs):
        '''Instantiate a Rollcall object from an R matrix, of the kind
        described in the pscl docs.
        See http://cran.r-project.org/web/packages/pscl/pscl.pdf
        '''
        return _RollcallTranslator(**kwargs).r_object(r_matrix)

    # Alternative constructors ------------------------------------------------
    @classmethod
    def from_dataframe(cls, dataframe, **kwargs):
        '''Instantiate a Rollcall object from a pandas.DataFrame corresponding
        to the R matrix described in the pscl docs.
        See http://cran.r-project.org/web/packages/pscl/pscl.pdf
        '''
        r_matrix = rpy_common.convert_to_r_matrix(dataframe)
        return cls.from_matrix(r_matrix, **kwargs)


class _RollcallTranslator(Translator):
    '''A python wrapper around the R pscl pacakge's rollcall object.
    '''
    r_type = pscl.rollcall
    wrapper = Rollcall

    yea = Field(name='yea', default=1)
    nay = Field(name='nay', default=2)
    not_in_legis = Field(name='notInLegis', default=9)
    field_names = (
        ('missing', 'missing'),
        ('legis_names', 'legis.names'),
        ('vote_names', 'vote.names'),
        ('legis_data', 'legis.data'),
        ('vote_data', 'vote.data'),
        ('desc', 'desc'),
        ('source', 'source'))

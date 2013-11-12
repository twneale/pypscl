import numpy as np
from pandas.rpy import common as rpy_common

from rpy2.robjects.packages import importr

from .base import Field, Translator, Wrapper
from .accessors import ValueAccessor, VectorAccessor
from .ordfile import OrdFile
from .wnominate import wnominate
from .ideal import ideal

pscl = importr('pscl')


class NumberOfLegislators(VectorAccessor):
    '''Number of legislators in the rollcall object, after processing the
    dropList.
    '''
    key = 'n'


class NumberOfRollcalls(VectorAccessor):
    '''Number of roll call votes in the rollcall object, after
    processing the dropList.
    '''
    key = 'm'


class AllVotes(VectorAccessor):
    '''A matrix containing a tabular breakdown of all votes in the
    rollcall matrix (object$votes), after processing the
    dropList.
    '''
    key = 'allVotes'


class Votes(VectorAccessor):
    '''
    '''


class Source(VectorAccessor):
    '''A fake, hard-coded C: filesystem location of the ord file. Useless.
    '''

class RollcallSummary(Wrapper):

    all_votes = AllVotes()
    n = NumberOfLegislators()
    m = NumberOfRollcalls()
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
    '''A wrapper for the pscl rollcall object.
    '''
    # Wrapped R functions ---------------------------------------------------
    def drop_unanimous(self, lop=0):
        self.obj = pscl.dropUnanimous(self.obj, lop=0)
        return self

    def summary(self):
        return RollcallSummary(pscl.summary_rollcall(self.obj))

    # Accessors ---------------------------------------------------------------
    n = NumberOfLegislators()
    m = NumberOfRollcalls()
    votes = Votes()
    source = Source()
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

    # Alternative constructors ------------------------------------------------
    @classmethod
    def from_matrix(cls, r_matrix, **kwargs):
        '''Instantiate a Rollcall object from an R matrix, of the kind
        described in the pscl docs.
        See http://cran.r-project.org/web/packages/pscl/pscl.pdf
        '''
        return _RollcallTranslator(**kwargs).r_object(r_matrix)

    @classmethod
    def from_dataframe(cls, dataframe, **kwargs):
        '''Instantiate a Rollcall object from a pandas.DataFrame corresponding
        to the R matrix described in the pscl docs.
        See http://cran.r-project.org/web/packages/pscl/pscl.pdf
        '''
        r_matrix = rpy_common.convert_to_r_matrix(dataframe)
        return cls.from_matrix(r_matrix, **kwargs)

    @classmethod
    def from_ordfile(cls, fp, **kwargs):
        '''Instantiate a RollCall object from an ordfile.
        '''
        dataframe = OrdFile(fp).as_dataframe()
        rollcall = cls.from_dataframe(dataframe,
            yea=[1.0, 2.0, 3.0],
            nay=[4.0, 5.0, 6.0],
            missing=[7.0, 8.0, 9.0],
            not_in_legis=0.0,
            legis_names=tuple(dataframe.index), **kwargs)
        return rollcall

    # Analysis methods -------------------------------------------------------
    def ideal(self, *args, **kwargs):
        '''
        '''
        return ideal(self, *args, **kwargs)

    def wnominate(self, polarity, *args, **kwargs):
        '''
        '''
        return wnominate(self, polarity, *args, **kwargs)



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

from rpy2.robjects.packages import importr

from .base import Field, CallTranslator, Wrapper
from .utils import Cached


pscl = importr('pscl')


def ideal(*args, **kwargs):
    return IdealCaller(*args, **kwargs).robject()


class Ideal(Wrapper):
    pass


class IdealCaller(CallTranslator):
    r_type = pscl.ideal
    wrapper = Ideal

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


from rpy2.robjects.packages import importr
import rpy2.robjects as robjects

from .base import Field, Builder, Wrapper
from .utils import Cached


pscl = importr('pscl')



class Ideal(Wrapper):

    @property
    def n(self):
        return list(self.n).pop()

    @property
    def m(self):
        return list(self.m).pop()

    @property
    def d(self):
        return list(self.m).pop()


class IdealCaller(Builder):
    r_type = pscl.ideal
    wrapper = Ideal

    obj = Field(name='object')
    codes = Field('codes')
    drop_list = Field(name='dropList')
    d = Field(name='d')
    maxiter = Field(name='maxiter')
    thin = Field(name='thin')
    burnin = Field(name='burnin')
    impute = Field(name='impute')
    mda = Field(name="mda")
    normalize = Field(name="normalize")
    meanzero = Field(name="meanzero")
    priors = Field(name="priors")
    startvals = Field(name="startvals")
    store_item = Field(name="store_item")
    file_ = Field(name="file")


def ideal(rollcall, **kwargs):
    return IdealCaller(obj=rollcall.obj, **kwargs).r_object()

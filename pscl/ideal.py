from rpy2.robjects.packages import importr

from .base import Translator, Wrapper
from .accessors import ValueAccessor, VectorAccessor


rpscl = importr('pscl')


class Ideal(Wrapper):

    n = ValueAccessor('n')
    m = ValueAccessor('m')
    d = ValueAccessor('d')
    all_votes = VectorAccessor('votes')

    eq_attrs = ('m', 'n', 'd', 'xbar')

    @property
    def xbar(self):
        leg_ids = tuple(self['xbar'].rownames)
        mcmc_values = tuple(self['xbar'])
        return dict(zip(leg_ids, mcmc_values))


class _IdealTranslator(Translator):
    r_type = rpscl.ideal
    wrapper = Ideal

    field_names = (
        ('obj', 'object'),
        ('codes', 'codes')    ,
        ('drop_list', 'dropList'),
        ('d', 'd'),
        ('maxiter', 'maxiter'),
        ('thin', 'thin'),
        ('burnin', 'burnin'),
        ('impute', 'impute'),
        ('mda', 'mda'),
        ('normalize', 'normalize'),
        ('meanzero', 'meanzero'),
        ('priors', 'priors'),
        ('startvals', 'startvals'),
        ('store_item', 'store_item'),
        ('file_', 'file'))


def ideal(rollcall, **kwargs):
    return _IdealTranslator(obj=rollcall.obj, **kwargs).r_object()

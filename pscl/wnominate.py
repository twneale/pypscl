from rpy2.robjects.packages import importr
from rpy2.robjects import r as rr

from .base import Translator, Wrapper, SubWrapper
from .accessors import LastVectorItemAccessor, VectorAccessor


r_wnominate = importr('wnominate')


class WnominateSummary(Wrapper):
    coord1D = VectorAccessor('coord1D')
    coord2D = VectorAccessor('coord2D')
    eq_attrs = ('coord1D', 'coord2D')


class _WnominateLegislators(SubWrapper):

    key = 'legislators'

    CC = VectorAccessor('CC')
    correct_yea = VectorAccessor('correctYea')
    correct_nay = VectorAccessor('correctNay')
    se1D = VectorAccessor('se1D')
    se2D = VectorAccessor('se2D')
    coord2D = VectorAccessor('coord2D')
    coord1D = VectorAccessor('coord1D')
    wrong_yea = VectorAccessor('wrongYea')
    wrong_nay = VectorAccessor('wrongNay')
    GMP = VectorAccessor('GMP')
    corr_1 = VectorAccessor('corr.1')

    # These fields are only present if your using one of the
    # ord files.
    state = VectorAccessor('state')
    cd = VectorAccessor('cd')
    party = VectorAccessor('party')
    icpsr_legis = VectorAccessor('icpsrLegis')
    iscpsr_state = VectorAccessor('icpsrState')
    party_code = VectorAccessor('partyCode')

    eq_attrs = (
        'CC', 'correct_yea', 'correct_nay', 'se1D', 'se2D', 'coord2D',
        'coord1D', 'wrong_yea', 'wrong_nay', 'GMP', 'corr_1', 'state',
        'cd', 'party', 'icpsr_legis', 'iscpsr_state', 'party_code')


class _WnominateRollcalls(SubWrapper):
    key = 'rollcalls'

    PRE = VectorAccessor('PRE')
    GMP = VectorAccessor('GMP')
    midpoint2D = VectorAccessor('midpoint2D')
    midpoint3D = VectorAccessor('midpoint3D')
    spread2D = VectorAccessor('spread2D')
    spread3D = VectorAccessor('spread3D')
    correct_yea = VectorAccessor('correctYea')
    correct_nay = VectorAccessor('correctNay')
    wrong_nay = VectorAccessor('wrongNay')
    wrong_yea = VectorAccessor('wrongYea')

    eq_attrs = (
        'PRE', 'GMP', 'midpoint2D', 'midpoint3D', 'spread2D', 'spread3D',
        'correct_yea', 'correct_nay', 'wrong_nay', 'wrong_yea', )


class Wnominate(Wrapper):
    dimensions = LastVectorItemAccessor('dimensions')
    eigenvalues = VectorAccessor('eigenvalues')
    beta = LastVectorItemAccessor('beta')
    weights = VectorAccessor('weights')
    fits = VectorAccessor('fits')

    legislators = _WnominateLegislators()
    rollcalls = _WnominateRollcalls()

    eq_attrs = (
        'dimensions', 'eigenvalues', 'beta', 'weights', 'fits',
        'legislators', 'rollcalls', )

    def __eq__(self, other):
        '''For some reason, 2 identical R datastructures don't compare is equal
        to each for me through rpy2. Necessary for unit tests to work.
        '''
        self.legislators == other.legislators
        self.rollcalls = other.rollcalls
        return tuple(self._get_eq_vals()) == tuple(other._get_eq_vals())

    def summary(self):
        return WnominateSummary(r_wnominate.summary_nomObject(self.obj))



class _WnominateTranslator(Translator):
    r_type = r_wnominate.wnominate
    wrapper = Wnominate
    field_names = (
        ('obj', 'rcObject'),
        ('ubeta', 'ubeta'),
        ('uweights', 'uweights'),
        ('dims', 'dims'),
        ('minvotes', 'minvotes'),
        ('lop', 'lop'),
        ('trials', 'trials'),
        ('polarity', 'polarity'),
        ('verbose', 'verbose'))


def wnominate(rollcall, polarity, **kwargs):
    return _WnominateTranslator(
        obj=rollcall.obj, polarity=polarity, **kwargs).r_object()

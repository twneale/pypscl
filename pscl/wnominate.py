from rpy2.robjects.packages import importr
from rpy2.robjects import r as rr

from .base import Translator, Wrapper, SubWrapper
from .accessors import ValueAccessor, VectorAccessor


r_wnominate = importr('wnominate')


# Accessors -----------------------------------------------------------------
class Coord1D(VectorAccessor):
    '''First dimension W-NOMINATE score.
    See http://cran.r-project.org/web/packages/wnominate/wnominate.pdf.
    '''
    key = 'coord1D'


class Coord2D(VectorAccessor):
    '''Second dimension W-NOMINATE score.
    See http://cran.r-project.org/web/packages/wnominate/wnominate.pdf.
    '''
    key = 'coord2D'


class CorrectClassification(VectorAccessor):
    '''The "correct classification." The wnominate docs don't make clear
    what this is.
    '''
    key = 'CC'


class CorrectYea(VectorAccessor):
    '''The wnominate docs described this as 'Predicted Yeas and Actual Yeas',
    which seems to imply two lists, of a list of 2-tuples. This attribute
    only returns a list of floats, though, so I don't get it.
    '''
    key = 'correctYea'


class WrongYea(VectorAccessor):
    '''The wnominate docs described this as 'Predicted Yeas and Actual Nays',
    which seems to imply two lists, of a list of 2-tuples. This attribute
    only returns a list of floats, though, so I don't get it.
    '''
    key = 'wrongYea'


class CorrectNay(VectorAccessor):
    '''The wnominate docs described this as 'Predicted Nays and Actual Nays',
    which seems to imply two lists, of a list of 2-tuples. This attribute
    only returns a list of floats, though, so I don't get it.
    '''
    key = 'correctNay'


class WrongNay(VectorAccessor):
    '''The wnominate docs described this as 'Predicted Yeas and Actual Yeas',
    which seems to imply two lists, of a list of 2-tuples. This attribute
    only returns a list of floats, though, so I don't get it.
    '''
    key = 'wrongNay'


class StandardError1D(VectorAccessor):
    '''Bootstrapped standard error of first dimension W-NOMINATE score.
    This will be empty if trials is set below 4.
    '''
    key = 'se1D'


class StandardError2D(VectorAccessor):
    '''Bootstrapped standard error of second dimension W-NOMINATE score.
    This will be empty if trials is set below 4.
    '''
    key = 'se2D'


class GeometricMeanProbability(VectorAccessor):
    '''The geometric mean probability (*GMP*), "which is computed as the
     anti-log of the average log-likelihood." Apparently this is explained
     in the origin Poole and Rosenthal paper.
     See http://harrisschool.uchicago.edu/Blogs/EITM/wp-content/uploads/2011/06/McCarty2010.pdf.
    '''
    key = 'GMP'


class Covariance(VectorAccessor):
    '''Covariance between first and second dimension W-NOMINATE score.
    '''
    key = 'corr.1'


# R object wrappers ---------------------------------------------------------
class WnominateSummary(Wrapper):
    coord1D = Coord1D()
    coord2D = Coord2D()
    eq_attrs = ('coord1D', 'coord2D')

class _WnominateLegislators(SubWrapper):
    '''Legislator-specific information from the wnominate object. Most
    attributes are vectors that correspond to the order of legislators
    in the data frame.
    '''
    key = 'legislators'

    CC = CorrectClassification()
    correct_yea = CorrectYea()
    correct_nay = CorrectNay()
    wrong_yea = WrongYea()
    wrong_nay = WrongNay()

    se1D = StandardError1D()
    se2D = StandardError2D()
    coord1D = Coord1D()
    coord2D = Coord2D()

    GMP = GeometricMeanProbability()
    corr_1 = Covariance()

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
    GMP = GeometricMeanProbability()
    midpoint2D = VectorAccessor('midpoint2D')
    midpoint3D = VectorAccessor('midpoint3D')
    spread2D = VectorAccessor('spread2D')
    spread3D = VectorAccessor('spread3D')
    correct_yea = CorrectYea()
    correct_nay = CorrectNay()
    wrong_nay = WrongNay()
    wrong_yea = WrongYea()

    eq_attrs = (
        'PRE', 'GMP', 'midpoint2D', 'midpoint3D', 'spread2D', 'spread3D',
        'correct_yea', 'correct_nay', 'wrong_nay', 'wrong_yea', )


class Dimensions(VectorAccessor):
    '''An integer representing the number of dimensions estimated.
    '''


class Eigenvalues(VectorAccessor):
    '''A list of rollcall eigenvalues. Somehow the size of the eigenvalues
    reflects the "dimensionality" of the voting.
    See http://cran.r-project.org/web/packages/wnominate/wnominate.pdf.
    '''

class Beta(VectorAccessor):
    '''The beta value used in the final W-NOMINATE iteration.
    '''

class Weights(VectorAccessor):
    '''A tuple of weights used in each W-NOMINATE iteration.
    '''

class Fits(VectorAccessor):
    '''A vector of length 3*dimensions with the classic measures of fit.
    In order, it contains the correct classiﬁcations for each dimension, the
    APREs for each dimension, and the overall GMPs for each dimension.
    '''

class Wnominate(Wrapper):
    dimensions = Dimensions()
    eigenvalues = Eigenvalues()
    beta = Beta()
    weights = Weights()
    fits = Fits()

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

    def plot(self):
        return r_wnominate.plot_nomObject(self.obj)

    def plot_coords(self):
        return r_wnominate.plot_coords(self.obj)

    def plot_angles(self):
        return r_wnominate.plot_angles(self.obj)


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

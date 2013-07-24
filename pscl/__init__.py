import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

from .rollcall import Rollcall, RollcallSummary
from .ideal import ideal
from .wnominate import wnominate, Wnominate, WnominateSummary
from .utils import Cached


class _Data(object):
    '''A lazy loader for example data.
    '''
    @Cached
    def _wnominate(self):
        return importr('wnominate')

    @Cached
    def _pscl(self):
        return importr('pscl')

    @property
    def sen90(self):
        self._wnominate
        return Rollcall(robjects.r('data(sen90); sen90'))

data = _Data()
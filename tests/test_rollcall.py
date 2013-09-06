from os.path import join, dirname, abspath
from unittest import TestCase

import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

from pscl.rollcall import Rollcall, RollcallSummary
from pscl.ideal import ideal, Ideal
from pscl.utils import cd
from pscl.ordfile import OrdFile


rpscl = importr('pscl')


class RollcallTest(TestCase):

    # Create the expected rollcall object directly from R.
    s109 = robjects.r('''
        s109
        ''')
    expected_rollcall = Rollcall(s109)

    # Wrap it in a pypscl Rollcall.
    expected_summary = RollcallSummary(robjects.r('summary.rollcall')(s109))

    # Now re-create an equivalent pypscl Rollcall object from the raw
    # ascii .ord file from which the built-in R s109 rollcall object was
    # origininall created.
    here = dirname(abspath(__file__))
    with cd(join(here, 'fixtures')):
        with open('sen109kh.ord') as f:
            rollcall = Rollcall.from_ordfile(f)

    summary = rollcall.summary()

    def test_summary(self):
        self.assertEquals(self.expected_summary, self.summary)

    def test_rollcall(self):
        self.assertEquals(self.expected_rollcall, self.rollcall)

    # def test_ideal(self):
    #     '''
    #     Test the pscl `ideal` function against our wrapped version.
    #     http://cran.r-project.org/web/packages/pscl/pscl.pdf.
    #     '''
    #     x = robjects.r('''
    #         idLong <- ideal(s109,
    #             d=1,
    #             priors=list(xpv=1e-12,bpv=1e-12),
    #             normalize=TRUE,
    #             store.item=FALSE,
    #             maxiter=260E3,
    #             burnin=10E3,
    #             thin=100,
    #             verbose=TRUE)
    #         ''')
    #     x = Ideal(x)

    #     f = ideal(
    #         self.expected_rollcall, d=1,
    #         priors=robjects.r('list(xpv=1e-12,bpv=1e-12)'),
    #         normalize=True,
    #         store_item=False, maxiter=260e3,
    #         burnin=10e3, thin=100,
    #         verbose=True)
    #     import nose.tools;nose.tools.set_trace()

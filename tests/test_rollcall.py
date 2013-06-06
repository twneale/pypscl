from os.path import join, dirname, abspath
from unittest import TestCase

import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

from pscl.rollcall import Rollcall, RollcallSummary
from pscl.ideal import ideal
from pscl.utils import cd
from pscl.ordfile import OrdFile


rpscl = importr('pscl')


class RollcallTest(TestCase):

    # Create the expected rollcall object directly from R.
    # Nuke the legis.data attribute to simplify things.
    s109 = robjects.r('''
        library(pscl)
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
        f = open('sen109kh.ord')
    ordfile = OrdFile(f)

    rollcall = ordfile.as_rollcall()
    summary = rollcall.summary()

    def test_summary(self):
        self.assertEquals(self.expected_summary, self.summary)

    def test_rollcall(self):
        self.assertEquals(self.expected_rollcall, self.rollcall)

    def test_ideal(self):
        '''
        Test the pscl `ideal` function against our wrapped version.
        http://cran.r-project.org/web/packages/pscl/pscl.pdf.
        '''
        xi = robjects.r('''
            n <- dim(s109$legis.data)[1]
            x0 <- rep(0,n)
            x0[s109$legis.data$party=="D"] <- -1
            x0[s109$legis.data$party=="R"] <- 1
            id1 <- ideal(
                s109,
                d=1,
                startvals=list(x=x0),
                normalize=TRUE,
                store.item=TRUE,
                maxiter=100,
                burnin=0,
                thin=10,
                verbose=TRUE)
            ''')

        fi = ideal(
            self.expected_rollcall, d=1, startvals=robjects.r('list(x=x0)'),
            normalize=True, store_item=True, maxiter=100,
            burnin=0, thin=10, verbose=True)
        import nose.tools;nose.tools.set_trace()

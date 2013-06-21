from os.path import join, dirname, abspath
from unittest import TestCase

import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

from pscl import Rollcall, RollcallSummary, wnominate, Wnominate
from pscl.utils import cd
from pscl.ordfile import OrdFile


r_wnominate = importr('wnominate')


class RollcallTest(TestCase):

    # Create the expected rollcall object directly from R.
    # Nuke the legis.data attribute to simplify things.
    sen90 = robjects.r('''
        data(sen90)
        sen90
        ''')
    expected_rollcall = Rollcall(sen90)

    # Wrap it in a pypscl Rollcall.
    expected_summary = RollcallSummary(robjects.r('summary.rollcall')(sen90))

    # Now re-create an equivalent pypscl Rollcall object from the raw
    # ascii .ord file from which the built-in R s109 rollcall object was
    # origininall created.
    here = dirname(abspath(__file__))
    with cd(join(here, 'fixtures')):
        f = open('sen90kh.ord')
    ordfile = OrdFile(f)

    rollcall = ordfile.as_rollcall()
    summary = rollcall.summary()

    r_script = 'wnominate(sen90, polarity=c(2, 5))'
    expected_wnominate = Wnominate(robjects.r(r_script))

    import nose.tools;nose.tools.set_trace()
    wnominate = rollcall.wnominate(polarity=(2, 5))

    def test_summary(self):
        self.assertEquals(self.expected_summary, self.summary)

    def test_rollcall(self):
        self.assertEquals(self.expected_rollcall, self.rollcall)

    def test_wnominate(self):
        self.assertEquals(self.expected_wnominate, self.wnominate)

import unittest

from Troubleshooting.report import Report


class TestReport(unittest.TestCase):

    def testCanInstantiate(self):
        r = Report()
        self.assertEqual('---', r.generate()[:3])

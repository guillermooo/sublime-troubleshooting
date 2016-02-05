import unittest
import os

from Troubleshooting.lib.subprocess import check_output


class Test_check_output(unittest.TestCase):

    @unittest.skipIf(os.name != 'nt', 'because only for Windows')
    def testCanReadOutput(self):
        expected = os.getcwd()
        actual = check_output(['echo', '%CD%'], shell=True, universal_newlines=True)
        self.assertEqual(expected, actual.strip())

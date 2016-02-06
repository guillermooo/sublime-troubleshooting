import unittest
import os
import sys

from Troubleshooting.lib.subprocess import check_output


class Test_check_output(unittest.TestCase):

    @unittest.skipIf(sys.platform != 'win32', 'because only for Windows')
    def testCanReadOutput(self):
        expected = os.getcwd()
        actual = check_output(['echo', '%CD%'], shell=True, universal_newlines=True)
        self.assertEqual(expected, actual.strip())

    @unittest.skipIf(sys.platform != 'darwin', 'because only for OS X')
    def testCanReadOutputInOsx(self):
        expected = 'Darwin'
        actual = check_output(['uname'], universal_newlines=True)
        self.assertEqual(expected, actual.strip())
     
import unittest

import sublime

from Troubleshooting.editor_info import EditorInfo


# add attribute to test this only on Sublime Text
class TestEditorInfo(unittest.TestCase):

    def testCanInstantiate(self):
        ei = EditorInfo.from_current()
        self.assertEqual('Editor Info', ei.title)
        self.assertEqual([], ei.elements)

    def testKnowsProviderName(self):
        ei = EditorInfo.from_current()
        self.assertEqual('Sublime Text API', ei.provider)

    def testCanCollectData(self):
        ei= EditorInfo.from_current()
        ei.collect()
        self.assertEqual(5, len(ei.elements))
        self.assertEqual("name=Sublime Text", str(ei.elements[0]))
        self.assertEqual("version={0}".format(sublime.version()), str(ei.elements[1]))
        self.assertEqual("architecture={0}".format(sublime.arch()), str(ei.elements[2]))
        self.assertEqual("channel={0}".format(sublime.channel()), str(ei.elements[3]))
        self.assertEqual("platform={0}".format(sublime.platform()), str(ei.elements[4]))

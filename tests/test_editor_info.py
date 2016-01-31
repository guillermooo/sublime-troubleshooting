import unittest

import sublime

from Troubleshooting.editor_info import EditorInfo


# add attribute to test this only on Sublime Text
class TestEditorInfo(unittest.TestCase):

    def testCanInstantiate(self):
        ei = EditorInfo.from_current_editor()
        self.assertEqual('Editor Info', ei.title)
        self.assertEqual([], ei.items)

    def testKnowsProviderName(self):
        ei = EditorInfo.from_current_editor()
        self.assertEqual('Sublime Text API', ei.provider)

    def testCanCollectData(self):
        ei= EditorInfo.from_current_editor()
        ei.collect()
        self.assertEqual(5, len(ei.items))
        self.assertEqual("name=Sublime Text", str(ei.items[0]))
        self.assertEqual("version={0}".format(sublime.version()), str(ei.items[1]))
        self.assertEqual("architecture={0}".format(sublime.arch()), str(ei.items[2]))
        self.assertEqual("channel={0}".format(sublime.channel()), str(ei.items[3]))
        self.assertEqual("platform={0}".format(sublime.platform()), str(ei.items[4]))

import unittest

import sublime

from Troubleshooting.plugin.editor_info import EditorInfo


# add attribute to test this only on Sublime Text
class TestEditorInfo(unittest.TestCase):

    def testCanInstantiate(self):
        ei = EditorInfo.from_current()
        self.assertEqual('Editor info', ei.title)
        self.assertEqual([], ei.elements)

    def testKnowsProviderName(self):
        ei = EditorInfo.from_current()
        self.assertEqual('Sublime Text API', ei.provider)

    def testCanCollectData(self):
        ei= EditorInfo.from_current()
        ei.collect()
        self.assertEqual(3, len(ei.elements))
        self.assertEqual("Version and architecture", ei.elements[0].title)
        self.assertEqual("View settings", str(ei.elements[1].title))

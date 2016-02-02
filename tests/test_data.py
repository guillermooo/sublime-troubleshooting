import unittest

from Troubleshooting.plugin.data import DataItem
from Troubleshooting.plugin.data import DataBlock


class TestDataItem(unittest.TestCase):

    def testCanInstantiate(self):
        di = DataItem('foo', 'bar')
        self.assertEqual('foo', di.name)
        self.assertEqual('bar', di.value)


class TestDataBlock(unittest.TestCase):

    def testCanInstantiate(self):
        db = DataBlock('foo')
        self.assertEqual(0, len(db.items))

    def testReturnsExpectedStringIfEmpty(self):
        db = DataBlock('foo')
        self.assertEqual('foo', str(db))

    def testReturnsExpectedString(self):
        db = DataBlock('foo', items=[DataItem('dog', 'fido')])
        self.assertEqual('foo\n\ndog=fido', str(db))
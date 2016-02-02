import unittest

from Troubleshooting.plugin.report import Report
from Troubleshooting.plugin.report import MarkDownWriterMixin


class TestReport(unittest.TestCase):

    def testCanInstantiate(self):
        r = Report()
        self.assertEqual('###', r.generate()[:3])


class Test_MarkDownWriterMixin(unittest.TestCase):

    def testCanInstantiate(self):
        m = MarkDownWriterMixin()
        self.assertIsNone(m.buf)

    def testCanQuote(self):
        buf = []
        m = MarkDownWriterMixin()
        with m.collect_markup(buf):
            m.quote('foo')
        self.assertEqual('> foo\n', ''.join(buf))

    def testCanWrite(self):
        buf = []
        m = MarkDownWriterMixin()
        with m.collect_markup(buf):
            m.write('foo')
        self.assertEqual('foo', ''.join(buf))        

    def testCanWriteLine(self):
        buf = []
        m = MarkDownWriterMixin()
        with m.collect_markup(buf):
            m.write_line('foo')
        self.assertEqual('foo\n', ''.join(buf))                

    def testCanH3(self):
        buf = []
        m = MarkDownWriterMixin()
        with m.collect_markup(buf):
            m.h3('foo')
        self.assertEqual('### foo\n', ''.join(buf))

    def testCanH5(self):
        buf = []
        m = MarkDownWriterMixin()
        with m.collect_markup(buf):
            m.h5('foo')
        self.assertEqual('##### foo\n', ''.join(buf))

    def testCanItalics(self):
        buf = []
        m = MarkDownWriterMixin()
        with m.collect_markup(buf):
            m.italics('foo')
        self.assertEqual('*foo*', ''.join(buf))

    def testCanBold(self):
        buf = []
        m = MarkDownWriterMixin()
        with m.collect_markup(buf):
            m.bold('foo')
        self.assertEqual('**foo**', ''.join(buf))        

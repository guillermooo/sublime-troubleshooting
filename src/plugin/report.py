import contextlib

from concurrent.futures import ThreadPoolExecutor

import sublime

from ..plugin.data import DataBlock
from ..plugin.data import DataItem
from ..plugin.data import UserDataSection
from ..plugin.editor_info import EditorInfo
from ..plugin.platform_info import PlatformInfo


class MarkDownWriterMixin(object):

    def __init__(self):
        # We can't start adding stuff right away, we need to call .collect_markup() first.
        self.buf = None

    def write(self, text):
        self.buf.append(text)

    def write_line(self, text=''):
        self.buf.append(text + '\n')

    def h3(self, text):
        self.write_line('### ' + text)

    def h5(self, text):
        self.write_line('##### ' + text)

    def quote(self, text):
        self.write_line('> ' + text)

    def italics(self, text):
        self.write('*{0}*'.format(text))

    def bold(self, text):
        self.write('**{0}**'.format(text))

    @contextlib.contextmanager
    def collect_markup(self, buf):
        assert isinstance(buf, list)
        old_buf = self.buf
        self.buf = buf
        yield
        self.buf = old_buf


class Report(MarkDownWriterMixin):

    def __init__(self):
        super().__init__()
        self.infos = []

        self.infos.append(EditorInfo.from_current())
        self.infos.append(PlatformInfo.from_current())

    def collect(self, callback=bool):
        executor = ThreadPoolExecutor(max_workers=1)
        futures = []
        for info in self.infos:
            future = executor.submit(info.collect)
            future.add_done_callback(callback)
            futures.append(future)
        return futures

    def generate(self):
        footer = '''---
This report was generated by the [Troubleshooting][self] package.

[self]: https://bitbucket.org/guillermooo/sublime-troubleshooting
'''
        description = UserDataSection("Problem description",
                                      "Please add as many destails as you can, including reproduction steps.")
        expected = UserDataSection("Expected behavior",
                                   "What did you expect to happen instead?")

        buf = []
        for i, info in enumerate([description, expected] + self.infos):
            if isinstance(info, UserDataSection):
                with self.collect_markup(buf):
                    self.h3(info.title)
                    self.write_line()
                    self.italics(info.description)
                    self.write_line()
                    self.write_line()
            else:
                if i == 2:  # print a separator after the user input sections
                    with self.collect_markup(buf):
                        self.write_line('---')

                with self.collect_markup(buf):
                    self.write_line()
                    self._collect_info_markup(info)
        buf.append('\n' + footer)
        return ''.join(buf)

    def _collect_info_markup(self, info):
        self.h3(info.title + ' (as provided by ' + info.provider + ')')
        if info.description:
            self.write_line()
            self.italics(info.description)
            self.write_line()
            self.write_line()

        for i, element in enumerate(info.elements):
            if isinstance(element, DataItem):
                self.quote('**' + element.name + ':** ' + str(element.value))
            elif isinstance(element, DataBlock):
                if i > 0:
                    self.write_line()
                self.h5(element.title)
                self.write_line()
                if element.description:
                    self.italics(element.description)
                    self.write_line()
                    self.write_line()
                for item in element.items:
                    self.quote('**' + item.name + ':** ' + str(item.value))


def show_progress(message, status_key, view=None):
    view = view if view else sublime.active_window().active_view()
    counter = 0
    # Pad with spaces so it reserves space in the status bar.
    spec = '{:<%d}' % (len(message) + 3)

    def progress():
        nonlocal counter

        if counter == -1:
            view.set_status(status_key, '')
            return

        counter += 1 % 1000
        view.set_status(status_key, spec.format(message + '.' * (counter % 3 + 1)))

        sublime.set_timeout(progress, 350)

    sublime.set_timeout(progress, 100)

    def dispose():
        nonlocal counter
        counter = -1

    return dispose

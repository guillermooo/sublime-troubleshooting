import sublime

import contextlib
import abc
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
from threading import Lock

from .editor_info import EditorInfo
from .platform_info import PlatformInfo
from .data import DataSection
from .data import DataItem
from .data import DataBlock


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

    def collect(self, cb=bool):
        executor = ThreadPoolExecutor(max_workers=1)
        futures = []
        for info in self.infos:
            future = executor.submit(info.collect)
            future.add_done_callback(cb)
            futures.append(future)
        return futures

    def generate(self):
        footer = '''---
This report was generated by the [Troubleshooting][self] package.

[self]: https://bitbucket.org/guillermooo/sublime-troubleshooting
'''
        buf = []
        for i, info in enumerate(self.infos):
            with self.collect_markup(buf):
                if i > 0:
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


def plugin_loaded():
    return
    def on_done(f):
        nonlocal countdown
        countdown -= 1
        if countdown == 0:
            dispose_progress()
            show(report)

    report = Report()

    dispose_progress = show_progress("Troubleshooting: Generating report")     
    countdown = len(report.infos)
    
    report.collect(on_done)    


def show(report):
    v = sublime.active_window().new_file()
    v.run_command('insert', {'characters': report.generate()})


def show_progress(message):
    view = sublime.active_window().active_view()
    counter = 0
    lock = Lock()

    def progress():
        nonlocal counter

        if counter == -1:
            view.set_status('ts.status', '')
            return

        counter += 1 % 1000
        spec = '{:<%d}' % (len(message) + 3)
        view.set_status('ts.status', spec.format(message + '.' * (counter % 3 + 1)))
        
        sublime.set_timeout(progress, 350)

    sublime.set_timeout(progress, 350)

    def dispose():
        nonlocal counter
        with lock:
            counter = -1    

    return dispose

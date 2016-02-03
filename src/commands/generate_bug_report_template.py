from threading import Lock

import sublime_plugin

from ..plugin.report import Report
from ..plugin.report import show_progress


class GenerateBugReportTemplateCommand(sublime_plugin.WindowCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = Lock()

    def run(self):
        def on_done(f):
            nonlocal countdown
            with self.lock:
                countdown -= 1
                if countdown == 0:
                    dispose_progress()
                    self.show(report)

        report = Report()

        dispose_progress = show_progress("Troubleshooting: Generating report",
                                         'ts.progress', self.window.active_view())
        countdown = len(report.infos)

        report.collect(on_done)

    def show(self, report):
        v = self.window.new_file()
        v.set_name("Bug Report for Sublime Text")
        v.run_command('insert', {'characters': report.generate()})

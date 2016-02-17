from threading import Lock
import os

import sublime_plugin

from ..plugin.report import Report
from ..plugin.report import show_progress


__all__ = (
   'GenerateBugReportTemplateCommand',
    )


class GenerateBugReportTemplateCommand(sublime_plugin.WindowCommand):
    """Generates a template for reporting a bug about Sublime Text. The template
    containes pre-filled system and editor data to help diagnose the issue.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = Lock()

    def run(self):
        def on_each_done(f):
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

        report.collect(on_each_done)

    def show(self, report):
        v = self.window.new_file()
        v.set_name("Bug Report for Sublime Text")
        v.run_command('insert_snippet', { 'contents': '$payload', 'payload': report.generate() })

        syntax = 'Packages/Markdown/Markdown.sublime-syntax'
        if not os.path.exists(syntax):
            syntax = 'Packages/Markdown/Markdown.tmLanguage'
        v.run_command('set_file_type', {'syntax': syntax})

        self._select_first_input_line(v)
        v.show(v.sel()[0])

    def _select_first_input_line(self, view):
        view.sel().clear()
        second_line = view.line(view.text_point(2, 0))
        view.sel().add(second_line)

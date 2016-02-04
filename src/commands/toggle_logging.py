from collections import defaultdict

import sublime
import sublime_plugin


__all__ = (
    'ToggleLoggingCommand',
    )


def show_status(view, key, message, duration=0):
    view.set_status(key, message)

    def dispose():
        view.set_status(key, '')

    if duration > 0:
        sublime.set_timeout(dispose, duration)

    return dispose


class ToggleLoggingCommand(sublime_plugin.WindowCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.states = defaultdict(lambda: False)

    def run(self, kind):
        state = self.states[kind]
        if kind == 'commands':
            sublime.log_commands(not state)
        elif kind == 'input':
            sublime.log_input(not state)
        else:
            show_status(self.window.active_view(),
                        'ts.status', 'Troubleshooting: Unknown kind of logging: "{}"'
                        .format(kind), duration=4000)
            return

        self.states[kind] = not state
        show_status(self.window.active_view(),
                    'ts.status', 'Troubleshooting: Logging staus for "{}" set to "{}"'
                    .format(kind, self.states[kind]), duration=4000)

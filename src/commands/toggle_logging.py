from collections import defaultdict

import sublime
import sublime_plugin


__all__ = (
    'ToggleLoggingCommand',
    )


def show_status(view, key, message, duration=0):
    view.set_status(key, message)

    def dispose():
        # Easy check to see if we are disposing the message we set.
        if view.get_status(key) == message:
            view.set_status(key, '')

    if duration > 0:
        sublime.set_timeout(dispose, duration)

    return dispose


logging_states = defaultdict(lambda: False)


class ToggleLoggingCommand(sublime_plugin.WindowCommand):
    """Toggles logging of different kinds.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = [
            'commands',
            'input',
            'commands+input',
            'build systems',
            'result regex',
            'build systems+result regex',
            'indexing',
            ]
        self.toggles = {
            'commands': lambda x: sublime.log_commands(x),
            'input': lambda x: sublime.log_input(x),
            'build systems': lambda x: sublime.log_build_systems(x),
            'result regex': lambda x: sublime.log_result_regex(x),
            'indexing': lambda x: sublime.log_indexing(x),
            }

    def run(self):
        items = [[o, ', '.join(str(logging_states[sub_o]) for sub_o in o.split("+"))]
                 for o in self.options]
        self.window.show_quick_panel(items, self.on_select)

    def on_select(self, index):
        if index == -1:
            return
        kinds = self.options[index]
        for kind in kinds.split('+'):
            try:
                state = logging_states[kind]
                self.toggles[kind](not state)
                logging_states[kind] = not state
            except KeyError:
                show_status(self.window.active_view(),
                            'ts.status', 'Troubleshooting: Unknown kind of logging: "{}"'
                            .format(kind), duration=4000)
                return

        fragment = '; '.join('logging %s: {}' % item for item in kinds.split('+'))
        show_status(self.window.active_view(),
                    'ts.status', ('Troubleshooting: ' + fragment)
                    .format(*[logging_states[kind] for kind in kinds.split('+')]), duration=4000)

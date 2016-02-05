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
        self.options = ['commands', 'input', 'commands+input', 'build systems', 'result regex', 'build systems+result regex']
        self.actions = {
            'commands': lambda x: sublime.log_commands(x),
            'input': lambda x: sublime.log_input(x),
            'build systems': lambda x: sublime.log_build_systems(x),
            'result regex': lambda x: sublime.log_result_regex(x),
        }

    def run(self):
        items = [[o, str(self.states[o]) if '+' not in o else '--'] for o in self.options]
        self.window.show_quick_panel(items, self.toggle)        

    def toggle(self, index):
        kinds = self.options[index]        
        for kind in kinds.split('+'):            
            try:
                state = self.states[kind]
                self.actions[kind](not state)
            except KeyError:
                show_status(self.window.active_view(),
                            'ts.status', 'Troubleshooting: Unknown kind of logging: "{}"'
                            .format(kind), duration=4000)
                return
            else:
                self.states[kind] = not state

        fragment = '; '.join('logging %s: {}' % item for item in kinds.split('+'))
        show_status(self.window.active_view(),
                    'ts.status', ('Troubleshooting: ' + fragment)
                    .format(*[self.states[kind] for kind in kinds.split('+')]), duration=4000)

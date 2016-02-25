import abc
import os
import json

import sublime

from .data import DataSection
from .data import DataItem
from .data import DataBlock
from .data import DataProvider
from .data import PreItem


# Information about a text editor.
class EditorInfo(DataProvider, DataSection):

    def __init__(self, *args, **kwargs):
        super().__init__('Editor info', *args, **kwargs)

    # Returns information about the currently running editor. This is the
    # only public API.
    @classmethod
    def from_current(cls):
        info = SublimeTextInfo()
        return info

    # Indicates where the information was extracted from.
    @property
    @abc.abstractmethod
    def provider(self):
        pass

    # TODO: Some providers will take long to generate data, so we need to notify the caller when
    # we are done in some way; probably via events. Also, display some visual indication when
    # some long-running op is in progress.
    # Collects data about the editor.
    @abc.abstractmethod
    def collect(self):
        pass


# Information about Sublime Text.
class SublimeTextInfo(EditorInfo):

    def __init__(self):
        super().__init__(description='General details about Sublime Text')

    @classmethod
    def from_current(cls):
        return cls()

    @property
    def provider(self):
        return 'Sublime Text API'

    def collect(self):
        self.elements.clear()

        db0 = DataBlock('Version and architecture')
        db0.items.append(DataItem('name', 'Sublime Text'))
        db0.items.append(DataItem('version', sublime.version()))
        db0.items.append(DataItem('architecture', sublime.arch()))
        db0.items.append(DataItem('channel', sublime.channel()))
        db0.items.append(DataItem('platform', sublime.platform()))

        view = sublime.active_window().active_view()
        view_settings = view.settings()

        db1 = DataBlock('View settings')
        for setting_name in ('syntax', 'tab_size', 'translate_tabs_to_spaces'):
            db1.items.append(DataItem(setting_name, view_settings.get(setting_name)))

        db2 = DataBlock('View state')
        db2.items.append(DataItem('is view dirty', view.is_dirty()))
        db2.items.append(DataItem('is view readonly', view.is_read_only()))
        db1.items.append(DataItem('encoding', view.encoding()))
        db1.items.append(DataItem('em width', view.em_width()))
        db1.items.append(DataItem('selection count', len(view.sel())))
        db1.items.append(DataItem('has non empty selections', view.has_non_empty_selection_region()))

        self.elements.append(db0)

        # TODO: Split the rest up into methods.
        self.collect_package_data()

        self.elements.append(db1)
        self.elements.append(db2)

        self.collect_profiling_data()

    def collect_package_data(self):
        block = DataBlock('Package data')

        _, packages, _ = next(os.walk(sublime.packages_path()))
        packages = list(packages)

        _, _, files = next(os.walk(sublime.installed_packages_path()))
        files = [f[:-16] for f in files if f.endswith('.sublime-package')]

        ignored_packages = sublime.load_settings('Preferences.sublime-settings').get('ignored_packages', [])

        block.items.append(DataItem('installed packages', json.dumps(files)))
        block.items.append(DataItem('packages', json.dumps(packages)))
        block.items.append(DataItem('ignored packages', json.dumps(ignored_packages)))

        self.elements.append(block)

    def collect_profiling_data(self):
        if sublime.version() < '3102':
            return

        from Default.profile import profile_text
        block = DataBlock('Profiling data (as reported by Default/profile.py)')
        block.items.append(PreItem(profile_text().strip()))
        self.elements.append(block)

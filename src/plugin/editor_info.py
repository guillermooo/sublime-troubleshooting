import abc
import os
import json

import sublime

from ..plugin.data import DataSection
from ..plugin.data import DataItem
from ..plugin.data import DataBlock
from ..plugin.data import DataProvider
from ..plugin.data import PreItem

from Default.profile import profile_text


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
        db1.items.append(DataItem('syntax', view_settings.get('syntax')))
        db1.items.append(DataItem('tab_size', view_settings.get('tab_size')))
        db1.items.append(DataItem('translate_tabs_to_spaces', view_settings.get('translate_tabs_to_spaces')))

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

        _, _, files = next(os.walk(sublime.installed_packages_path()))
        files = (f for f in files if f.endswith('.sublime-package'))

        ignored_packages = sublime.load_settings('Preferences.sublime-settings')

        block.items.append(DataItem('installed packages', json.dumps(list(files))))
        block.items.append(DataItem('packages', json.dumps(list(packages))))
        block.items.append(DataItem('ignored packages', json.dumps(ignored_packages.get('ignored_packages'))))

        self.elements.append(block)

    def collect_profiling_data(self):
        block = DataBlock('Profiling data (as reported by Default/profile.py)')

        block.items.append(PreItem(profile_text().strip()))

        self.elements.append(block)

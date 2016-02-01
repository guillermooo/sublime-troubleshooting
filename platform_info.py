import abc

import sublime

from .data import DataSection
from .data import DataItem
from .data import DataBlock
from .data import DataProvider


# Information about an OS.
class PlatformInfo(DataProvider, DataSection):

    def __init__(self, *args, **kwargs):
        super().__init__('Platform info', *args, **kwargs)

    # Returns information about the currently running editor. This is the
    # only public API.
    @classmethod
    def from_current(cls):
        info = WindowsInfo()
        info.collect()
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
class WindowsInfo(PlatformInfo):

    def __init__(self):
        super().__init__(description='Details about the current platform')

    @classmethod
    def from_current(cls):
        return self

    @property
    def provider(self):
        return 'systeminfo.exe'

    def collect(self):
        self.elements.clear()

        db0 = DataBlock('Version and architecture')
        db0.items.append(DataItem('name', 'Windows 10 Pro'))
        db0.items.append(DataItem('version', '10000'))
        db0.items.append(DataItem('architecture', 'x64'))

        db1 = DataBlock('Other')
        db1.items.append(DataItem('Hyper-V enabled', 'true'))

        self.elements.append(db0)
        self.elements.append(db1)

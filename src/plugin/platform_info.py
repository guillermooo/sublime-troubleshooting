import abc
2
from subprocess import TimeoutExpired

from ..lib.subprocess import check_output

from ..plugin.data import DataSection
from ..plugin.data import DataItem
from ..plugin.data import DataBlock
from ..plugin.data import DataProvider



# Information about an OS.
class PlatformInfo(DataProvider, DataSection):

    def __init__(self, *args, **kwargs):
        super().__init__('Platform info', *args, **kwargs)

    # Returns information about the currently running editor. This is the
    # only public API.
    @classmethod
    def from_current(cls):
        info = WindowsInfo()
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
        return cls()

    @property
    def provider(self):
        return 'systeminfo.exe'

    def call_and_parse(self, cmd):
        try:
            output = check_output(cmd, universal_newlines=True, timeout=30)
        except TimeoutExpired:
            return {}

        data = {}
        for line in (item for item in output.split('\n') if item):
            if not line.startswith(' '):
                head, tail = line.split(':', 1)
                data[head.strip().upper()] = tail.strip()
        return data

    def collect(self):
        data = self.call_and_parse(['systeminfo.exe'])

        if not data:
            self.elements.append(DataBlock('No data retrieved'))
            return

        self.elements.clear()

        db0 = DataBlock('Version and architecture')
        db0.items.append(DataItem('name', data['OS NAME']))
        db0.items.append(DataItem('version', data['OS VERSION']))
        db0.items.append(DataItem('architecture', data['SYSTEM TYPE']))
        db0.items.append(DataItem('OS build type', data['OS BUILD TYPE']))
        db0.items.append(DataItem('OS configuration', data['OS CONFIGURATION']))

        db1 = DataBlock('Local information')
        db1.items.append(DataItem('input locale', data['INPUT LOCALE']))
        db1.items.append(DataItem('system locale', data['SYSTEM LOCALE']))

        db2 = DataBlock('System information')
        db2.items.append(DataItem('windows directory', data['WINDOWS DIRECTORY']))
        db2.items.append(DataItem('total physical memory', data['TOTAL PHYSICAL MEMORY']))
        db2.items.append(DataItem('available physical memory', data['AVAILABLE PHYSICAL MEMORY']))
        db2.items.append(DataItem('virtual memory', data['VIRTUAL MEMORY']))
        db2.items.append(DataItem('page file location(s)', data['PAGE FILE LOCATION(S)']))

        self.elements.append(db0)
        self.elements.append(db1)
        self.elements.append(db2)

import sys
import abc
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
        plat = sys.platform
        if plat == 'win32':
            info = WindowsInfo()
        elif plat == 'darwin':
            info = UnixInfo()
        else:
            info = UnixInfo()
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
        return 'systeminfo.exe and wmic.exe'

    def call(self, cmd, shell=False):
        try:
            return check_output(cmd, universal_newlines=True, timeout=30, shell=shell)
        except TimeoutExpired:
            pass

    def collect(self):
        self.collect_systeminfo_data()
        self.collect_wmic_data()

    def collect_wmic_data(self):
        buf = []

        cmds = [
            'wmic desktopmonitor get pixelsperxlogicalinch /value',
            'wmic desktopmonitor get pixelsperylogicalinch /value',
        ]

        for cmd in cmds:
            try:
                output = self.call(cmd.split())
            except FileNotFoundError:
                self.elements.append(DataBlock('Could not find wmic.exe'))
                return
            if not output.strip():
                continue
            buf.append(output.strip())

        if not buf:
            self.elements.append(DataBlock('No data retrieved from wmic.exe'))
            return

        db0 = DataBlock('Display information')
        for item in buf:
            db0.items.append(DataItem(*item.split('=')))

        self.elements.append(db0)

    def collect_systeminfo_data(self):
        try:
            output = self.call(['systeminfo.exe'])
        except FileNotFoundError:
            self.elements.append(DataBlock('Could not find systeminfo.exe'))
            return

        if not output:
            self.elements.append(DataBlock('No data retrieved from systeminfo.exe'))
            return

        data = {}
        for line in (item for item in output.split('\n') if item):
            if not line.startswith(' '):
                head, tail = line.split(':', 1)
                data[head.strip().upper()] = tail.strip()

        self.elements.clear()

        db0 = DataBlock('Version and architecture')
        db0.items.append(DataItem('name', data['OS NAME']))
        db0.items.append(DataItem('version', data['OS VERSION']))
        db0.items.append(DataItem('architecture', data['SYSTEM TYPE']))
        db0.items.append(DataItem('OS build type', data['OS BUILD TYPE']))
        db0.items.append(DataItem('OS configuration', data['OS CONFIGURATION']))

        db1 = DataBlock('Locale information')
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


# Information about Sublime Text.
class UnixInfo(PlatformInfo):

    def __init__(self):
        super().__init__(description='Details about the current platform')

    @classmethod
    def from_current(cls):
        return cls()

    @property
    def provider(self):
        return 'command line tools'

    def call(self, cmd, shell=False):
        try:
            return check_output(cmd, universal_newlines=True, timeout=30, shell=shell)
        except TimeoutExpired:
            pass

    def collect(self):
        self.collect_uname_data()
        self.collect_display_data()

    def collect_display_data(self):
        output = check_output(["system_profiler", "-detailLevel", "mini", "SPDisplaysDataType"], universal_newlines=True)

        if not output:
            return

        lines = output.split('\n')
        data = [line.split(':', 1) for line in lines if ':' in line]
        data = { k.strip().upper(): v.strip() for k, v in data if k.strip() and v.strip() }

        db0 = DataBlock('Display information')
        db0.items.append(DataItem("resolution", data['RESOLUTION']))
        db0.items.append(DataItem("pixel depth", data['PIXEL DEPTH']))

        self.elements.append(db0)

    def collect_uname_data(self):
        buf = []

        # TODO: Check if user can repeat keys fast
        # TODO: Add information about useful tools like the step recorder
        # TODO: Generate purely informational status reports for users

        cmds = [
            ('system name', 'uname -s'),
            ('system architecture', 'uname -m'),
            ('system version', 'uname -r'),
            ('processor', 'uname -p'),
        ]

        for desc, cmd in cmds:
            try:
                output = '{}={}'.format(desc, self.call(cmd.split()))
            except FileNotFoundError:
                self.elements.append(DataBlock('Could not find command'))
                return
            except Exception as e:
                self.elements.append(DataBlock('Error running command: %s' % e))
                return

            if not output.strip():
                continue
            buf.append(output.strip())

        if not buf:
            self.elements.append(DataBlock('No data retrieved'))
            return

        db0 = DataBlock('System information')
        for item in buf:
            db0.items.append(DataItem(*item.split('=')))

        self.elements.append(db0)

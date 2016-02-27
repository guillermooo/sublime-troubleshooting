import sys
import abc
from subprocess import TimeoutExpired

from ..lib.subprocess import check_output
from ..lib.logging import Logger

from .data import DataSection
from .data import DataItem
from .data import DataBlock
from .data import DataProvider


_l = Logger.from_module(__name__)


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
        return 'wmic.exe'

    def call(self, cmd, shell=False):
        try:
            return check_output(cmd, universal_newlines=True, timeout=30, shell=shell)
        except TimeoutExpired:
            _l.debug('timeout expired while gathering data')
        except FileNotFoundError:
            raise
        except Exception as e:
            _l.debug('unexpected exception while gathering data: %s', e)

    def collect(self):
        self.collect_systeminfo_data()
        self.collect_display_data()

    def collect_wmic_data(self, cmds, block_title):
        buf = []
        for cmd in cmds:
            try:
                output = self.call(cmd.split())
            except FileNotFoundError:
                self.elements.append(DataBlock('Could not find wmic.exe'))
                _l.error('wmic.exe does not appear to be present on the system')
                return
            except Exception:
                self.elements.append(DataBlock('Error while calling wmic.exe'))
                return
            if not output.strip():
                continue
            buf.append(output.strip())

        if not buf:
            self.elements.append(DataBlock('No data retrieved from wmic.exe'))
            _l.debug('no data retrieved from wmic.exe')
            return

        db0 = DataBlock('Display information')
        for item in buf:
            for line in filter(None, item.splitlines()):
                db0.items.append(DataItem(*line.split('=')))

        self.elements.append(db0)

    def collect_display_data(self):
        buf = []

        cmds = [
            'wmic desktopmonitor get pixelsperxlogicalinch /value',
            'wmic desktopmonitor get pixelsperylogicalinch /value',
        ]

        self.collect_wmic_data(cmds, 'Display Information')

    def collect_systeminfo_data(self):
        buf = []

        # TODO: add useful pieces of data / remove useless ones
        cmds = [
            'wmic os get osarchitecture /value',
            'wmic os get version /value',
            'wmic os get buildnumber /value',
            'wmic os get buildtype /value',
            'wmic os get caption /value',
            'wmic os get freephysicalmemory /value',
            'wmic os get freespaceinpagingfiles /value',
            'wmic os get freevirtualmemory /value',
        ]

        self.collect_wmic_data(cmds, 'Operating System Information')

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
            _l.debug('timeout expired while gathering data')
        except Exception as e:
            _l.debug('unexpected error while gathering data: %s', e)

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
                _l.error('could not find command %s', cmd)
                self.elements.append(DataBlock('Could not find command'))
                return
            except Exception as e:
                _l.error('error running command %s: %s', cmd, e)
                self.elements.append(DataBlock('Error running command: %s' % e))
                return

            if not output.strip():
                continue
            buf.append(output.strip())

        if not buf:
            self.elements.append(DataBlock('No data retrieved'))
            _l.debug('no data')
            return

        db0 = DataBlock('System information')
        for item in buf:
            db0.items.append(DataItem(*item.split('=')))

        self.elements.append(db0)

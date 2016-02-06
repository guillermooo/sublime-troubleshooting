import sys
import subprocess as sp

from subprocess import Popen
from subprocess import PIPE

try:
    from subprocess import STARTUPINFO
    from subprocess import STARTF_USESHOWWINDOW
    from subprocess import SW_HIDE
except ImportError:
    STARTUPINFO = None
    STARTF_USESHOWWINDOW = None
    SW_HIDE = None


def check_output(args, shell=False, universal_newlines=False, timeout=None):
    """Reads a process' output. On Windows, it supresses the console window.
    """

    if not sys.platform == 'win32':
        return sp.check_output(args, shell=shell, universal_newlines=universal_newlines, timeout=timeout)

    startup_info = STARTUPINFO()
    startup_info.dwFlags = STARTF_USESHOWWINDOW | SW_HIDE

    proc = Popen(args, stdout=PIPE, stderr=PIPE, shell=shell, universal_newlines=universal_newlines,
                 startupinfo=startup_info)
    data, err = proc.communicate(timeout=timeout)

    return data or err

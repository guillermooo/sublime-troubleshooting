import sys
import subprocess as sp

from subprocess import Popen
from subprocess import PIPE

__all__ = (
    'check_output',
)


if sys.platform == 'win32':
    import ctypes
    from subprocess import STARTUPINFO
    from subprocess import STARTF_USESHOWWINDOW
    from subprocess import SW_HIDE

    def check_output(args, shell=False, universal_newlines=False, timeout=None):
        """Conveniently read a process's output on Windows.

        Supresses the console window
        and handles decoding the binary stream
        with the 'correct' codepage.
        """
        startup_info = STARTUPINFO()
        startup_info.dwFlags = STARTF_USESHOWWINDOW | SW_HIDE

        # universal_newlines causes the output to be interpreted as `locale.getpreferredencoding()`,
        # which doesn't work at times
        # because console (OEM?) applications usually use a different encoding instead.
        # For example,
        # 850 for Western Europe,
        # 437 for English
        # and 936 for Chinese.
        proc = Popen(args, stdout=PIPE, stderr=PIPE, shell=shell, universal_newlines=False,
                     startupinfo=startup_info)
        data, err = proc.communicate(timeout=timeout)

        binary_output = data or err
        if not universal_newlines:
            return binary_output
        # Determine encoding.
        # Normally we would be able to get the encoding with `sys.stdout.encoding`,
        # but sublime.py overrides `sys.stdout` with a custom writer.
        # Do some "guessing" instead and replace chars we cannot decode.
        num_encoding = ctypes.windll.kernel32.GetOEMCP()
        if num_encoding:
            encoding = 'cp{}'.format(num_encoding)
        else:
            # Fall back to the "default" behavior,
            # but still replace instead of failing.
            # https://docs.python.org/3.3/library/subprocess.html#frequently-used-arguments
            import locale
            encoding = locale.getpreferredencoding(False)

        print("decoding binary output with encoding", encoding)
        output = binary_output.decode(encoding, 'replace')
        output = output.replace('\r\n', '\n')  # do the rest of universal_newlines's job
        return output

else:
    check_output = sp.check_output

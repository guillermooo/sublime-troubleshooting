import sys
import subprocess as sp

from subprocess import Popen
from subprocess import PIPE

from .logging import Logger

__all__ = (
    'check_output',
)


_l = Logger.from_module(__name__)


if sys.platform == 'win32':
    import ctypes
    from subprocess import STARTUPINFO
    from subprocess import STARTF_USESHOWWINDOW
    from subprocess import SW_HIDE


    startup_info = STARTUPINFO()
    startup_info.dwFlags = STARTF_USESHOWWINDOW | SW_HIDE


    def _check_output(args, shell=False, universal_newlines=False, timeout=None):
        """Conveniently read a process's output on Windows.

        Supresses the console window and decodes the binary stream using the
        console's codepage.
        """
        # universal_newlines causes the output to be interpreted as `locale.getpreferredencoding()`,
        # which doesn't work at times because console (OEM?) applications usually use a different
        # encoding instead. For example, 850 for Western Europe, 437 for English and 936 for Chinese.
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
            # Fall back to the "default" behavior, but still replace instead of failing.
            # https://docs.python.org/3.3/library/subprocess.html#frequently-used-arguments
            import locale
            encoding = locale.getpreferredencoding(False)

        _l.debug("decoding binary output with encoding %s", encoding)
        try:
            output = binary_output.decode(encoding)
        except UnicodeDecodeError:
            _l.debug('decoding error; replacing bad characters')
            output = binary_output.decode(encoding, 'replace')
        except Exception:
            _l.exception('unexpected error while decoding output')
            output = ''
        finally:
            output = output.replace('\r\n', '\n')  # do the rest of universal_newlines's job
            # wmic likes to output '\r\r\n', so we just replace all '\r'
            output = output.replace('\r', '')
            return output.strip()
else:
    _check_output = sp.check_output


def check_output(args, shell=False, universal_newlines=False, timeout=None):
    _l.debug("running %s; shell=%s; universal_newlines=%s;", args, shell, universal_newlines)
    output = _check_output(args, shell, universal_newlines, timeout)
    _l.debug("check_output result: %r", output)
    return output

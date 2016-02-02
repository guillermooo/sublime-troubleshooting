import os
import contextlib

from subprocess import call

from pybuilder.core import use_plugin
from pybuilder.core import task


SUBLIME_TEXT_DATA_PATH = os.environ.get('SUBLIME_TEXT_DATAX')

# use_plugin("python.core")
# use_plugin("python.unittest")
# use_plugin("python.coverage")
# use_plugin("python.distutils")

@task
def greet():
    print("hello")


@task
def develop():
    if os.name != 'nt':
        print("not implemented for OS '%s'", os.name)
        return

    if not (SUBLIME_TEXT_DATA_PATH and os.path.exists(SUBLIME_TEXT_DATA_PATH)):
        print(r"Can't locate the Data folder. Please set %SUBLIME_TEXT_DATA%.")
        return

    with cd(SUBLIME_TEXT_DATA_PATH) as old:
        _make_junction(old)        


@contextlib.contextmanager
def cd(new):
    old = os.getcwd()
    os.chdir(new)
    yield old
    os.chdir(old)


def _remove_junctions():
    if os.path.exists('Troubleshooting'):
        call(['rd', 'Troubleshooting'], shell=True)

    if os.path.exists('Troubleshootingtests'):
        call(['rd', 'Troubleshootingtests'], shell=True)


def _make_junction(base):
    _remove_junctions()
    call(['cmd', '/c', 'mklink', '/J', 'Troubleshooting', os.path.join(base, 'src')], shell=True)
    call(['cmd', '/c', 'mklink', '/J', 'Troubleshootingtests', os.path.join(base, 'tests')], shell=True)


default_task = "greet"

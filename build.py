import os
import contextlib

from subprocess import call

from pybuilder.core import use_plugin
from pybuilder.core import task
from pybuilder.core import init


SUBLIME_TEXT_DATA_PATH = os.environ.get('SUBLIME_TEXT_DATA')

# use_plugin("python.core")
# use_plugin("python.unittest")
# use_plugin("python.coverage")
# use_plugin("python.distutils")
use_plugin("python.flake8")

@init
def initialize(project):
    project.version = "0.0.1"
    project.set_property('dir_source_main_python', 'src')


@task
def develop():
    if os.name != 'nt':
        print("not implemented for OS '%s'", os.name)
        return

    if not (SUBLIME_TEXT_DATA_PATH and os.path.exists(SUBLIME_TEXT_DATA_PATH)):
        print(r"Can't locate the Data folder. Please set %SUBLIME_TEXT_DATA%.")
        return

    with cd(os.path.join(SUBLIME_TEXT_DATA_PATH, 'Packages')) as old:
        _make_junction(old)


@task
def undevelop():
    if os.name != 'nt':
        print("not implemented for OS '%s'", os.name)
        return

    if not (SUBLIME_TEXT_DATA_PATH and os.path.exists(SUBLIME_TEXT_DATA_PATH)):
        print(r"Can't locate the Data folder. Please set %SUBLIME_TEXT_DATA%.")
        return

    with cd(os.path.join(SUBLIME_TEXT_DATA_PATH, 'Packages')) as old:
        _remove_junctions(old)


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


default_task = "analyze"

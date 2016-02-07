import os
import sys
import contextlib

from subprocess import call

from pybuilder.core import use_plugin
from pybuilder.core import task
from pybuilder.core import init


SCRIPT_DIR = os.path.dirname(__file__)

if sys.platform == 'win32':
    SUBLIME_TEXT_DATA_PATH = os.environ.get('SUBLIME_TEXT_DATA')
elif sys.platform == 'darwin':
    SUBLIME_TEXT_DATA_PATH = os.path.expanduser('~/Library/Application Support/Sublime Text 3')
else:
    SUBLIME_TEXT_DATA_PATH = os.path.expanduser('~/.config/sublime-text-3')

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
    if sys.platform == 'win32':
        if not (SUBLIME_TEXT_DATA_PATH and os.path.exists(SUBLIME_TEXT_DATA_PATH)):
            print(r"Can't locate the Data folder. Please set %SUBLIME_TEXT_DATA%.")
            return
    elif sys.platform != 'darwin':
        print("not implemented for OS '%s'" % sys.platform)
        return

    with cd(os.path.join(SUBLIME_TEXT_DATA_PATH, 'Packages')):
        _make_links(SCRIPT_DIR)


@task
def undevelop():
    if sys.platform == 'win32':
        if not (SUBLIME_TEXT_DATA_PATH and os.path.exists(SUBLIME_TEXT_DATA_PATH)):
            print(r"Can't locate the Data folder. Please set %SUBLIME_TEXT_DATA%.")
            return
    elif sys.platform != 'darwin':
        print("not implemented for OS '%s'", os.name)
        return

    with cd(os.path.join(SUBLIME_TEXT_DATA_PATH, 'Packages')):
        _remove_links()


default_task = "analyze"

# Utils ///////////////////////////////////////////////////////////////////////

@contextlib.contextmanager
def cd(new):
    old = os.getcwd()
    try:
        os.chdir(new)
        yield old
    finally:
        os.chdir(old)


def link_folder(link, target):
    if sys.platform == 'win32':
        call(['cmd', '/c', 'mklink', '/J', link, target], shell=True)
    else:
        os.symlink(target, link, target_is_directory=True)


def remove_link(link):
    if sys.platform == 'win32':
        call(['rd', link], shell=True)
    else:
        try:
            os.unlink(link)
        except FileNotFoundError:
            pass


def _remove_links():
    remove_link('Troubleshooting')
    remove_link('Troubleshootingtests')


def _make_links(base):
    _remove_links()

    link_folder('Troubleshooting', os.path.join(base, 'src'))
    link_folder('Troubleshootingtests', os.path.join(base, 'tests'))

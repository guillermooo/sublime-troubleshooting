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
    # TODO: locate the path to ST from running process if any.
    if sys.platform == 'win32':
        if not (SUBLIME_TEXT_DATA_PATH and os.path.exists(SUBLIME_TEXT_DATA_PATH)):
            print(r"Can't locate the Data folder. Please set %SUBLIME_TEXT_DATA%.")
            return

    with cd(os.path.join(SUBLIME_TEXT_DATA_PATH, 'Packages')):
        rm_folder_link('Troubleshooting')
        rm_folder_link('Troubleshootingtests')
        link_folder('Troubleshooting', os.path.join(SCRIPT_DIR, 'src'))
        link_folder('Troubleshootingtests', os.path.join(SCRIPT_DIR, 'tests'))


@task
def undevelop():
    if sys.platform == 'win32':
        if not (SUBLIME_TEXT_DATA_PATH and os.path.exists(SUBLIME_TEXT_DATA_PATH)):
            print(r"Can't locate the Data folder. Please set %SUBLIME_TEXT_DATA%.")
            return

    with cd(os.path.join(SUBLIME_TEXT_DATA_PATH, 'Packages')):
        rm_folder_link('Troubleshooting')
        rm_folder_link('Troubleshootingtests')


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


def rm_folder_link(link):
    try:
        os.unlink(link)
    except FileNotFoundError:
        pass

import os

import sublime


def get_user_packages():
    try:
        _, packages, _ = next(os.walk(sublime.packages_path()))
    except StopIteration:
        return set()
    return set(packages)


def get_installed_packages():
    return _package_archives_at(sublime.installed_packages_path())


def get_default_packages():
    default_path = os.path.join(os.path.dirname(sublime.executable_path()), "Packages")
    return _package_archives_at(default_path)


def _package_archives_at(path):
    try:
        _, _, files = next(os.walk(path))
    except StopIteration:
        return set()
    suffix = '.sublime-package'
    return {f[:-len(suffix)] for f in files if f.endswith(suffix)}

import sublime
import sublime_plugin

from ..lib.packages import get_user_packages, get_installed_packages, get_default_packages
from ..lib.logging import Logger


PACKAGE_NAME, _, _ = __package__.partition(".")
EXCLUDED_PACKAGES = {'User', PACKAGE_NAME}
DEFAULT_SETTINGS = {
    'syntax': 'Packages/Text/Plain text.tmLanguage',
    'color_scheme': None,  # 'Monokai.sublime-color-scheme',
    'theme': None,  # 'Default.sublime-theme',
}
WIDGET_SETTINGS = {
    "Console Input Widget.sublime-settings",
    "Regex Widget.sublime-settings",
    "Regex Format Widget.sublime-settings",
    "Regex Replace Widget.sublime-settings",
    "Widget.sublime-settings",
}
BACKUP_PREFIX = "ts_"


logger = Logger.from_module(__name__)


def _packages_to_disable():
    all_user_packages = get_user_packages() | get_installed_packages()
    return all_user_packages - get_default_packages() - EXCLUDED_PACKAGES


def _package_from_resource_path(res_path):
    if not res_path.startswith('Packages/'):
        return None
    try:
        return res_path.split('/', 2)[1]
    except IndexError:
        return None


def _packages_with_resource(res_name):
    res_paths = sublime.find_resources(res_name)
    packages = {_package_from_resource_path(res_path) for res_path in res_paths}
    packages.discard(None)
    return packages


def _backup_setting(settings, name):
    """Copy old value to a backup name and set a default value."""
    new_name = BACKUP_PREFIX + name
    settings.set(new_name, settings.get(name))
    default = DEFAULT_SETTINGS[name]
    if default is None:
        settings.erase(name)
    else:
        settings.set(name, DEFAULT_SETTINGS[name])


def _restore_setting(settings, name):
    """Copy backed up value to real name and erase backup."""
    old_name = BACKUP_PREFIX + name
    settings.set(name, settings.get(old_name))
    settings.erase(old_name)


def _get_referenced_packages(settings, name):
    """Return a set of packages that the resource "path" references.

    Type-specific checks are BACKUP_PREFIX-aware.
    """
    packages = set()
    value = settings.get(name)
    if not value:
        return packages

    type_ = name if not name.startswith(BACKUP_PREFIX) else name[2:]
    if type_ in ('theme', 'color_scheme'):
        packages |= _packages_with_resource(value)
    if type_ in ('color_scheme', 'syntax'):
        package = _package_from_resource_path(value)
        if package:
            packages.add(package)

    return packages


def _safe_disable(packages):
    """Disable packages "safely" by removing any existing references to its resources.

    Checks for theme, color_scheme, and syntax paths.

    TODO dictionary?
    """
    prefs = sublime.load_settings("Preferences.sublime-settings")

    # Always do global first as they might propagate
    for name in ('theme', 'color_scheme'):
        if _get_referenced_packages(prefs, name) & packages:
            logger.debug("Backing up global %r with value %r", name, prefs.get(name))
            _backup_setting(prefs, name)
            # Skip saving; we'll do it at the end

    for window in sublime.windows():
        # Skip project settings because they are … hopefully not as important
        for view in window.views():
            settings = view.settings()
            for name in ('color_scheme', 'syntax'):
                if _get_referenced_packages(settings, name) & packages:
                    logger.debug("Backing up view's %r with value %r (%s)",
                                 name, prefs.get(name), view.file_name())
                    _backup_setting(settings, name)

    for widget_settings in WIDGET_SETTINGS:
        # We assume that we won't need to fix theme-specific widgets,
        # as the theme was already changed and thus they'd be disabled.
        wdg_prefs = sublime.load_settings(widget_settings)
        changed = False
        for name in ('color_scheme', 'syntax'):
            if _get_referenced_packages(wdg_prefs, name) & packages:
                logger.debug("Backing up widget's %r with value %r (%s)",
                             name, wdg_prefs.get(name), widget_settings)
                _backup_setting(wdg_prefs, name)
                changed = True
        if changed:
            sublime.save_settings(widget_settings)

    # Preparation done
    old_ignored = prefs.get('ignored_packages', [])
    new_ignored = set(old_ignored) | packages
    prefs.set('ignored_packages', list(sorted(new_ignored)))
    sublime.save_settings("Preferences.sublime-settings")


def _reenable(packages):
    prefs = sublime.load_settings("Preferences.sublime-settings")
    old_ignored = prefs.get('ignored_packages', [])
    new_ignored = packages - set(old_ignored)
    prefs.set('ignored_packages', list(sorted(new_ignored)))
    sublime.save_settings("Preferences.sublime-settings")
    # Pray nothing breaks here

    # Order doesn't really matter here, but global first still makes the most sense
    for name in ('theme', 'color_scheme'):
        backup_name = BACKUP_PREFIX + name
        if _get_referenced_packages(prefs, backup_name) & packages:
            logger.debug("Restoring global %r to %r", name, prefs.get(backup_name))
            _restore_setting(prefs, name)
            # Skip saving; we'll do it at the end

    for window in sublime.windows():
        for view in window.views():
            settings = view.settings()
            for name in ('color_scheme', 'syntax'):
                backup_name = BACKUP_PREFIX + name
                if _get_referenced_packages(settings, backup_name) & packages:
                    # View-specific settings are unlikely,
                    # so we just erase the original instead of resetting.
                    logger.debug("Restoring view's %r by erasing (%s)", name, view.file_name())
                    settings.erase(name)
                    settings.erase(backup_name)

    for widget_settings in WIDGET_SETTINGS:
        wdg_prefs = sublime.load_settings(widget_settings)
        changed = False
        for name in ('color_scheme', 'syntax'):
            backup_name = BACKUP_PREFIX + name
            if _get_referenced_packages(wdg_prefs, backup_name) & packages:
                logger.debug("Restoring widget's %r to %r (%s)",
                             name, wdg_prefs.get(name), widget_settings)
                changed = True
        if changed:
            sublime.save_settings(widget_settings)

    # All done
    sublime.save_settings("Preferences.sublime-settings")


class TsDisableAllPackages(sublime_plugin.WindowCommand):

    """Disable all user packages (except 'User' and this one)."""

    def is_enabled(self):
        prefs = sublime.load_settings("Preferences.sublime-settings")
        return not bool(prefs.get(BACKUP_PREFIX + 'ignored_packages'))

    def run(self):
        # Store lists/config globally and across sessions
        prefs = sublime.load_settings("Preferences.sublime-settings")
        old_ignored = prefs.get('ignored_packages')
        prefs.set(BACKUP_PREFIX + 'ignored_packages', old_ignored)

        to_disable = _packages_to_disable()
        if not to_disable:
            sublime.message_dialog("There are no packages to disable.")
            return

        _safe_disable(to_disable)

        sublime.message_dialog("{} packages have been disabled."
                               " It is highly suggested to restart Sublime Text"
                               " to ensure that all packages have unloaded properly."
                               .format(len(to_disable)))


class TsReenableAllPackages(sublime_plugin.WindowCommand):

    """Reenable previously disabled packages."""

    def is_enabled(self):
        prefs = sublime.load_settings("Preferences.sublime-settings")
        return bool(prefs.get(BACKUP_PREFIX + 'ignored_packages'))

    def run(self):
        prefs = sublime.load_settings("Preferences.sublime-settings")

        ignored = prefs.get('ignored_packages')
        new_ignored = prefs.get(BACKUP_PREFIX + 'ignored_packages')
        prefs.erase(BACKUP_PREFIX + 'ignored_packages')

        to_enable = set(ignored) - set(new_ignored)
        _reenable(to_enable)

        sublime.message_dialog("{} packages have been enabled."
                               .format(len(to_enable)))

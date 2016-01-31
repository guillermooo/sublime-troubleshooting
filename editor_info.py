import sublime


from Troubleshooting.data import DataSection
from Troubleshooting.data import DataItem


# Information about a text editor.
class EditorInfo(DataSection):

    def __init__(self, *args, **kwargs):
        super().__init__('Editor Info', *args, **kwargs)

    # Returns information about the currently running editor. This is the
    # only public API.
    @classmethod
    def from_current_editor(cls):
        return SublimeTextInfo()

    # Indicates where the information was extracted from.
    @property
    def provider(self):
        raise TypeError("don't instantiate %s" % self.__class__.__name__)

    # Collects data about the editor.
    def collect(self):
        raise TypeError("don't instantiate %s" % self.__class__.__name__)


# Information about Sublime Text.
class SublimeTextInfo(EditorInfo):

    def __init__(self):
        super().__init__(description='General details about Sublime Text')

    @classmethod
    def from_current_editor(cls):
        return self

    @property
    def provider(self):
        return 'Sublime Text API'

    def collect(self):
        self.elements.clear()
        self.elements.append(DataItem('name', 'Sublime Text'))
        self.elements.append(DataItem('version', sublime.version()))
        self.elements.append(DataItem('architecture', sublime.arch()))
        self.elements.append(DataItem('channel', sublime.channel()))
        self.elements.append(DataItem('platform', sublime.platform()))

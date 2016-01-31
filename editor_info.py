import sublime


from Troubleshooting.data import DataSection
from Troubleshooting.data import DataItem


# Information about a text editor.
class EditorInfo(DataSection):

    def __init__(self, *args, **kwargs):
        super().__init__('Editor info', *args, **kwargs)

    # Returns information about the currently running editor. This is the
    # only public API.
    @classmethod
    def from_current_editor(cls):
        info = SublimeTextInfo()
        info.collect()
        return info

    # Indicates where the information was extracted from.
    @property
    def provider(self):
        raise TypeError("don't instantiate %s" % self.__class__.__name__)

    # TODO: Some providers will take long to generate data, so we need to notify the caller when
    # we are done in some way; probably via events. Also, display some visual indication when
    # some long-running op is in progress.
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

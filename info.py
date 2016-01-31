import sublime


class MarkdownReportSnippetGeneratorMixin(object):

    def generate_markdown_snippet(self):
        pass


class EditorInfo(MarkdownReportSnippetGeneratorMixin):

    @property
    def editor_name(self):
        pass

    @property
    def version(self):
        pass

    @property
    def channel(self):
        pass

    @property
    def architecture(self):
        pass

    def generate_markdown_snippet(self):
        return '''{0} info:

> version: {1}
> channel: {2}
> architecture: {3}'''.format(self.editor_name, self.version, self.channel, self.architecture)

    def __str__(self):
        return self.generate_markdown_snippet()


class SublimeTextInfo(EditorInfo):

    @property
    def editor_name(self):
        return "Sublime Text"

    @property
    def version(self):
        return sublime.version()

    @property
    def channel(self):
        return sublime.channel()

    @property
    def architecture(self):
        return sublime.arch()


class PlatformInfo(MarkdownReportSnippetGeneratorMixin):

    @property
    def source(self):
        pass

    @property
    def product_name(self):
        pass

    @property
    def version(self):
        pass

    @property
    def architecture(self):
        pass

    def generate_markdown_snippet(self):
        return '''Plaform info (as reported by {0}):

> product name: {1}
> version: {2}
> architecture: {3}'''.format(self.source, self.product_name, self.version, self.architecture)

    def __str__(self):
        return self.generate_markdown_snippet()


class WindowsInfo(PlatformInfo):

    @property
    def source(self):
        return "systeminfo.exe"

    @property
    def product_name(self):
        return 'Windows 10 Pro'

    @property
    def version(self):
        return '10.10.10.10 Build 101010'

    @property
    def architecture(self):
        return 'x64'


class Report(object):

    def __init__(self):
        self._infos = []

    def append(self, info):
        self._infos.append(info)

    def extend(self, infos):
        self._infos.extend(infos)

    def generate(self):
        buf = []
        for info in self._infos:
            buf.append(str(info))
        return ''.join(buf)


def plugin_loaded():
    report = Report()
    report.extend([SublimeTextInfo(), WindowsInfo()])
    print(report.generate())

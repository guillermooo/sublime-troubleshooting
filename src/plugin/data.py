import abc


class DataProvider(metaclass=abc.ABCMeta):

    @classmethod
    @abc.abstractmethod
    def from_current(cls):
        pass

    # Indicates where the information was extracted from.
    @property
    @abc.abstractmethod
    def provider(self):
        pass

    # TODO: Some providers will take long to generate data, so we need to notify the caller when
    # we are done in some way; probably via events. Also, display some visual indication when
    # some long-running op is in progress.
    # Collects data about the editor.
    @abc.abstractmethod
    def collect(self):
        pass

# TODO: make this a named tuple?
class DataItem(object):

    def __init__(self, name, value, description=''):
        self.name = name
        self.value = value
        self.description = description

    def __str__(self):
        return '{0}={1}'.format(self.name, self.value)


class DataBlock(object):

    def __init__(self, title, description='', items=None):
        self.title = title
        self.description = description
        self.items = items or []

    def __str__(self):
        title = [self.title] if not self.items else [self.title + '\n']
        return '\n'.join(title + [str(item) for item in self.items])


class DataSection(object):

    def __init__(self, title, description='', elements=None):
        self.title = title
        self.description = description
        # An element can be a DataItem or a DataBlock.
        self.elements = elements or []

    def __str__(self):
        title = [self.title] if not self.elements else [title + '\n']
        return '\n'.join(title + [str(block) for block in self.elements])


class UserDataSection(DataSection):

    def __init__(self, title, description):
        super().__init__(title, description)

    @property
    def items(self, value):
        raise TypeError('cannot have items')

    @items.setter
    def items(self, value):
        raise TypeError('cannot have items')
    
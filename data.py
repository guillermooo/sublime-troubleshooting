

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

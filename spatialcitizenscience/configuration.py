from contextlib import contextmanager
from pathlib import Path
import yaml

def as_stream(stream_or_path, mode='r'):
    """
    Makes a stream from the given stream, filename or Path
    :param stream_or_path:
    :param mode: the file open mode r|w
    :return: an open stream
    """
    if isinstance(stream_or_path, Path):
        return stream_or_path.open(mode=mode, encoding='utf-8')

    elif isinstance(stream_or_path, str):
        return open(stream_or_path, mode=mode, encoding='utf-8')
    else:
        return stream_or_path


@contextmanager
def stream_scope(stream_or_path, mode='r'):
    stream = as_stream(stream_or_path, mode=mode)
    yield stream
    if hasattr(stream, 'close'):
        stream.close()


class Config(dict):

    @classmethod
    def find_home(cls):
        paths = [Path(p) / 'config.yml' for p in ('.', 'app', '/app')]
        for path in paths:
            if path.exists():
                cls.__home = path.parent
                return path.parent
        raise FileNotFoundError('Did not find any of: ' + ', '.join(str(p) for p in paths))

    @classmethod
    def set_home(cls, config_home):
        cls.__home = Path(config_home)

    __home = Path('.')

    def __dir__(self):
        return self.keys()

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f'This Config() does not contain {item}')

    def __init__(self, home=None, **kwargs):
        super().__init__(**kwargs)
        self.__home = Path(home or Config.__home)

    def __str__(self):
        return yaml.dump(self)

    def __repr__(self):
        return f'Config()'

    def load(self, filename: str = None):
        """
        Loads a yaml configuration file as an object structure
        :param filename: filename in the directory
        :param dir: pathlib.Path pointing to the directory of the config file, default=preferences
        :return: ordereddict.AttrDict with the data from the file
        """
        if not filename:
            filename = 'config.yml'

        if (f := self.__home / filename).exists():
            filename = f
        elif (f := Path(filename)).exists():
            filename = f
        else:
            raise FileNotFoundError(f'File {filename} not found')

        with filename.open(encoding='utf-8') as f:
            data = yaml.load(f, Loader=ConfigYAMLLoader)
            self.update(data)

        self.__home = Path(filename).parent
        return self

    @property
    def home(self) -> Path:
        return self.__home

    def __enter__(self):
        return self.load()

    def __exit__(self, exc_type, exc_val, exc_tb):
        ...

from yaml import Loader, MappingNode
from yaml.constructor import ConstructorError
from yaml.representer import Representer, SafeRepresenter


def from_yaml(loader, node):
    'Load mapping as AttrDict, preserving order'
    # Based on yaml.constructor.SafeConstructor.construct_mapping()
    config = Config()
    yield config
    if not isinstance(node, MappingNode):
        raise ConstructorError(
            None, None, 'expected a mapping node, but found %s' % node.id, node.start_mark)
    loader.flatten_mapping(node)
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=False)
        try:
            hash(key)
        except TypeError as exc:
            raise ConstructorError(
                'while constructing a mapping', node.start_mark,
                'found unacceptable key (%s)' % exc, key_node.start_mark)
        config[key] = loader.construct_object(value_node, deep=False)


class ConfigYAMLLoader(Loader):
    '''A YAML loader that loads mappings into ordered AttrDict.
    >>> config = yaml.load('x: 1, y: 2', Loader=ConfigYAMLLoader)
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_constructor(u'tag:yaml.org,2002:map', from_yaml)
        self.add_constructor(u'tag:yaml.org,2002:omap', from_yaml)


def to_yaml(dumper, data):
    'Convert AttrDict to dictionary, preserving order'
    # yaml.representer.BaseRepresenter.represent_mapping sorts keys if the
    # object has .items(). So instead, pass the items directly.
    return dumper.represent_mapping(u'tag:yaml.org,2002:map', data.items())


SafeRepresenter.add_representer(Config, to_yaml)
SafeRepresenter.add_multi_representer(Config, to_yaml)

Representer.add_representer(Config, to_yaml)
Representer.add_multi_representer(Config, to_yaml)
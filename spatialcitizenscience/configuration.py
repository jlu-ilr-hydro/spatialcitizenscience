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


home = Path(__file__).parent


preferences_dir = home


class Config(dict):

    def __dir__(self):
        return self.keys()

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f'This Config() does not contain {item}')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self):
        return yaml.dump(self)

    def __repr__(self):
        return f'Config()'

    def load(self, filename: str = None, dir: Path = preferences_dir):
        """
        Loads a yaml configuration file as an object structure
        :param filename: filename in the directory
        :param dir: pathlib.Path pointing to the directory of the config file, default=preferences
        :return: ordereddict.AttrDict with the data from the file
        """
        if not filename:
            filename = 'config.yaml'
        fn = dir / filename
        with open(fn) as f:
            data = yaml.load(f, Loader=ConfigYAMLLoader)
        return data

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
from contextlib import contextmanager
from pathlib import Path
import yaml
from orderedattrdict import AttrDict, yamlutils


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


def from_yaml(stream_or_path):
    """
    Loads yaml from a stream, path or filename as an orderedattrdict
    :param stream_or_path: A stream, Path or filename(str)
    :return: orderedattrdict.AttrDict
    """
    with stream_scope(stream_or_path) as stream:
        return yaml.load(stream, Loader=yamlutils.AttrDictYAMLLoader)

def to_yaml(data, stream_or_path=None):
    """
    Converts data to yaml.
    :param data:
    :param stream_or_path: A stream, path or filename or None to return a string
    :return:
    """
    with stream_scope(stream_or_path, mode='w') as stream:
        return yaml.dump(data, stream, default_flow_style=False)


home = Path(__file__).parent

preferences_dir = home


def get_config(filename: str = None, dir: Path = preferences_dir) -> AttrDict:
    """
    Loads a yaml configuration file as an object structure
    :param filename: filename in the directory
    :param dir: pathlib.Path pointing to the directory of the config file, default=preferences
    :return: ordereddict.AttrDict with the data from the file
    """
    if not filename:
        filename = 'config.yaml'
    fn = dir / filename
    data = from_yaml(fn)
    return data

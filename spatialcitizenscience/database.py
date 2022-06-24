import sqlite3
from datetime import datetime
import geojson
from collections.abc import Mapping
# from .configuration import get_config
import os


debug = False

python_to_sql_type = dict(
    str='TEXT',
    int='INTEGER',
    float='REAL',
    bytes='BLOB',
    datetime='TEXT'
)

str_to_python_type = dict(
    str=str, int=int, float=float, bytes=bytes, datetime=datetime
)


class Entry(Mapping):

    def __init__(self, fieldnames, *values):
        self._fieldnames = ['id'] + list(fieldnames)
        self._values = list(values)

    def __dir__(self):
        return self._fieldnames

    def __getattr__(self, item):
        if item in self._fieldnames:
            return self._values[self._fieldnames.index(item)]
        else:
            raise AttributeError(f'This entry has no field {item}')

    def __getitem__(self, item):
        if item in self._fieldnames:
            return self._values[self._fieldnames.index(item)]
        elif item in range(len(self._values)):
            return self._values[item]
        else:
            raise KeyError(f'This entry has no field or item position {item}')

    def __len__(self):
        return len(self._fieldnames)

    def __iter__(self):
        return iter(self._fieldnames)

    def __repr__(self):
        return 'Entry(' + ', '.join(f'{f}={v!r}' for f, v in zip(self._fieldnames, self._values)) + ')'

    def getlist(self, key, type=None):
        if not type:
            return [self[key]]
        else:
            return type([self[key]])


class Connection:
    """
    Wraps a sqlite connection for use with the field definition model
    """
    def __init__(self, config):
        if config.database.filename == ':memory:':
            self.__connection = sqlite3.connect(':memory:')
        else:
            self.__connection = sqlite3.connect(config.home / config.database.filename)

        self.tablename = config.database.tablename
        self.fields = config.database.fields
        self.fields = config.database.fields
        self.fieldnames = [f.name for f in self.fields]
        self.create()

    def create(self):
        """
        Creates the tables for the database
        :param config: The database configuration (get_config().database)
        :return:
        """
        columns = ',\n'.join(
            ['    {name} {type}'
                .format(name=col.name, type=python_to_sql_type[col.type])
             for col in self.fields])

        cmd = ('CREATE TABLE IF NOT EXISTS {tablename} (' +
               '\n    id INTEGER PRIMARY KEY AUTOINCREMENT,' +
               '\n{columns}\n);').format(
            tablename=self.tablename,
            columns=columns)

        if debug:
            print(cmd)

        c = self.execute(cmd)
        if debug:
            print('    ->', c.fetchall())

    def __enter__(self):
        """
        Helper function to use in a context:
        >>> with Connection() as con:
        >>>     pass
        :return:
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.__connection.rollback()
        else:
            self.__connection.commit()
        self.__connection.close()

    def execute(self, cmd, args=()):
        """
        Executes a SQL command
        :param cmd: The SQL command
        :param args: the arguments of the SQL command
        :return:
        """
        return self.__connection.execute(cmd, args)

    def write_entry(self, **kwargs):
        """
        Writes an entry into the database
        :param kwargs: A dictionary of fieldnames to new values
        :return:
        """
        values = [kwargs.get(f) for f in self.fieldnames]
        cmd = 'INSERT INTO {tn} ({fields}) VALUES ({values})'.format(
            tn=self.tablename,
            fields=', '.join([f.name for f in self.fields]),
            values=','.join('?' * len(self.fields))
        )
        if debug:
            print(cmd)

        c = self.execute(cmd, values)
        if debug:
            print('    ->', c.fetchall())

    def update_entry(self, id, **kwargs):
        values = [kwargs[k] for k in kwargs if k in self.fieldnames]
        fields = [k for k in kwargs if k in self.fieldnames]
        set_clause = ', '.join(f'{f}=?' for f in fields)
        cmd = f'UPDATE {self.tablename}\n   SET {set_clause}\n   WHERE id=?'.format(
            tn=self.tablename,
        )
        if debug:
            print(cmd)
            print(values, [id])

        c = self.execute(cmd, values + [id])
        if debug:
            print('    ->', c.fetchall())


    def commit(self):
        """
        Commits a Database action
        """
        self.__connection.commit()

    def count(self):
        """
        Returns the number of entries
        """
        cmd = 'SELECT count(*) FROM ' + self.tablename
        if debug:
            print(cmd)

        c = self.execute(cmd)
        r = c.fetchone()
        if debug:
            print('    ->', r)
        return r[0]

    def read_entries(self, **kwargs):
        """
        Returns all database entries. Needs more work on the filter
        :param kwargs: Filter, eg. id=10
        :return:
        """
        cmd = 'SELECT * FROM ' + self.tablename
        if kwargs:
            fields, values = zip(*kwargs.items())
            cmd += '\nWHERE\n    '
            cmd += ' AND \n    '.join(('{}=?'.format(k) for k in fields))
        else:
            values = ()
        cmd += ';'

        if debug:
            print(cmd)

        c = self.execute(cmd, values)
        for row in c:
            yield Entry(self.fieldnames, *row)

    def features(self):
        def make_feature_from_row(entry):
            p = geojson.Point([entry.lon, entry.lat])
            f = geojson.Feature(entry[0], p, properties=dict(entry))
            return f

        for entry in self.read_entries():
            yield make_feature_from_row(entry)


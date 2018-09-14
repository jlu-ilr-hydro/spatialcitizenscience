import sqlite3
from contextlib import contextmanager

from configuration import get_config
debug = False

python_to_sql_type = dict(
    str='TEXT',
    int='INTEGER',
    float='REAL',
    bytes='BLOB',
    datetime='TEXT'
)


class Connection:

    def __init__(self, config=None):
        config = config or get_config().database
        self.tablename = config.tablename
        self.__connection = sqlite3.connect(config.filename)
        self.fields = config.fields
        self.fieldnames = [f.name for f in self.fields]

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
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__connection.close()

    def execute(self, cmd, args=()):
        return self.__connection.execute(cmd, args)

    def write_entry(self, **kwargs):
        """
        Writes an entry into the database
        :param kwargs:
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

    def commit(self):
        self.__connection.commit()

    def count(self):
        cmd = 'SELECT count(*) FROM ' + self.tablename
        if debug:
            print(cmd)

        c = self.execute(cmd)
        r = c.fetchone()
        if debug:
            print('    ->', r)
        return r[0]

    def read_entries(self, **kwargs):
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
        return c.fetchall()


import unittest
import random
import spatialcitizenscience.database as db
from spatialcitizenscience.configuration import get_config, home


class TestConfig(unittest.TestCase):
    def test_config_file(self):
        self.assertTrue((home / 'config.yaml').exists())

    def test_config_entry(self):
        config = get_config()
        self.assert_('database' in config)
        self.assert_('content' in config)


def make_entry(config):
    return {f.name: random.random() * 100
            for f in config.fields
            }


class TestDb(unittest.TestCase):

    def test_init_db(self):
        config = get_config()
        config.database.filename = ':memory:'
        with db.Connection('', config.database) as con:
            con.create()

    def test_write_db(self):
        config = get_config()
        config.database.filename = ':memory:'
        with db.Connection('', config.database) as con:
            con.create()
            entry = make_entry(config.database)
            con.write_entry(**entry)
            con.commit()
            self.assertEqual(con.count(), 1)

    def test_read_db(self):
        config = get_config()
        config.database.filename = ':memory:'
        with db.Connection('', config.database) as con:
            con.create()
            for i in range(100):
                entry = make_entry(config.database)
                con.write_entry(**entry)
            con.commit()
            self.assertEqual(con.count(), 100)
            result = list(con.read_entries())
            self.assertEqual(len(result), 100)
            self.assertCountEqual([r[0] for r in result], range(1, 101))
            result = list(con.read_entries(id=10))
            self.assertEqual(len(result), 1, 'Filtered for id=10 but got too many results (or None)')



import unittest


from configuration import get_config, home

class TestConfig(unittest.TestCase):
    def test_config_file(self):
        self.assertTrue((home / 'config.yaml').exists())

    def test_config_entry(self):
        config = get_config()
        self.assert_('database' in config)
        db_conf = config.database
        self.assertEqual(db_conf.filename, 'entries.sqlite')
        self.assertEqual(db_conf.tablename, 'entries')
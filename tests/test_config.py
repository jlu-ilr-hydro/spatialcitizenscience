import unittest
from spatialcitizenscience.configuration import Config, home


class TestConfig(unittest.TestCase):
    def test_config_file(self):
        self.assertTrue((home / 'config.yaml').exists())

    def test_config_load(self):
        with Config() as config:
            _ = str(config)

    def test_config_attributes(self):
        with Config() as config:
            self.assertTrue(config.title)
            self.assertTrue(type(config.database) is Config)
            for f in config.database.fields:
                for item in ('name', 'type'):
                    self.assertTrue(item in f, f'database: a field misses a "{item}" attribute')
            self.assertTrue(type(config.content) is Config)




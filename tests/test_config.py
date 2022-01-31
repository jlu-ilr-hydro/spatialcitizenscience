
import pytest
import random

from spatialcitizenscience.configuration import Config
from spatialcitizenscience import database as db


config_content ="""
title: test-config
favicon: images/favicon.ico
database:
  filename: ':memory:'
  tablename: entries
  fields:
    - name: lat
      type: float
      description: °N
      notnull: true
    - name: lon
      type: float
      description: °E
      notnull: true
    - name: time
      type: datetime
      description: Date / Time
      notnull: true
    - name: comment
      type: str
      description: Comment
      notnull: true

content:
  index:
    title: Index
    text: main.md
  about:
    title: About
    text: about.md

map:
  title: Karte
  lon: 51.1
  lat: 9.8
  zoomlevel: 6
  location_btn: get current location
  location_msg: Make new entry

SECRET_KEY: change.me
"""


@pytest.fixture
def config_file(tmpdir):
    (tmpdir / 'config.yml').write_text(config_content, encoding='utf-8')
    return str(tmpdir)


def test_config_load(config_file):
    with Config(config_file) as config:
        assert config


def test_config_attributes(config_file):
    with Config(config_file) as config:
        assert config.title == 'test-config'
        assert type(config.database) is Config
        for f in config.database.fields:
            for item in ('name', 'type'):
                assert item in f, f'database: a field misses a "{item}" attribute'
        assert isinstance(config.content, Config)


def make_entry(config):
    return {f.name: random.random() * 100
            for f in config.fields
            }


class TestDb:

    def test_init_db(self, config_file):
        with Config(config_file) as config:
            with db.Connection(config) as con:
                ...

    def test_write_db(self, config_file):
        with Config(config_file) as config:
            with db.Connection(config) as con:
                entry = make_entry(config.database)
                con.write_entry(**entry)
                con.commit()
                assert con.count() == 1, f'Expected a single entry in database, found {con.count()}'

    def test_read_db(self, config_file):
        with Config(config_file) as config:
            config.database.filename = ':memory:'
            with db.Connection(config) as con:
                con.create()
                for i in range(100):
                    entry = make_entry(config.database)
                    con.write_entry(**entry)
                con.commit()
                assert con.count() == 100, f'Created 100 entries in database, but found {con.count()}'
                result = list(con.read_entries())
                assert len(result) == 100, f'Found {len(result)} entries, but 100 were created'
                result = list(con.read_entries(id=10))
                assert len(result) == 1, 'Filtered for id=10 but got too many results (or None)'




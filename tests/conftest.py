import pytest


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
    text: index.md
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

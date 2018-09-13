from sqlite3 import connect
from configuration import get_config
def write_entry(lon: float, lat: float, length: float, width: float, depth:float, comment:str) -> int:
    config = get_config()

    with connect(config.database) as con:
        con.execute(f'INSERT INTO {tn} (lon, lat, )'.format(...))

from sqlite3 import connect
from configuration import get_config


def write_entry(lon: float, lat: float, length: float, width: float, depth:float, comment:str) -> int:
    config = get_config()
    dbconf = config.database
    values = lon, lat, length, width, depth, comment
    with connect(dbconf.filename) as con:
        con.execute(f'INSERT INTO {tn} ({fields}) VALUES ({values})'.format(
            tn=dbconf.tablename,
            fields=', '.join(dbconf.fields),
            values=','.join('?' * len(dbconf.fields))
        ),
            values

        )

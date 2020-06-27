import sqlite3
from lib.common.Util import *


def create_sqlite_db():
    db_path = os.path.join(get_db_path(), "test.db")
    conn_sqlite3 = sqlite3.connect(db_path)
    cursor = conn_sqlite3.cursor()
    sql_table = "create table myTable (id varchar(20) primary key, name varchar(30), password varchar(30))"
    cursor.execute(sql_table)

    sql_value_01 = 'INSERT  INTO  myTable(name,password) VALUES("city","19")'
    cursor.execute(sql_value_01)

    cursor.close()
    conn_sqlite3.commit()
    conn_sqlite3.close()


# Main test
if __name__ == '__main__':
    # create_sqlite_db()
    debug_print(datetime.now())


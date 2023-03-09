import sqlite3


def drop_table_db(tbl_name):
    con = sqlite3.connect('database/multi_db.db')
    cur = con.cursor()
    cur.execute(f'DROP TABLE IF EXISTS {tbl_name}')
    con.commit()
    con.close()


if __name__ == '__main__':
    # drop_db('multiplication')
    drop_table_db('users')
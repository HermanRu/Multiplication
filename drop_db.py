import sqlite3


def drop_db(tbl_name):
    con = sqlite3.connect('multi_db.db')
    cur = con.cursor()
    cur.execute(f'DROP TABLE IF EXISTS {tbl_name}')
    con.commit()
    con.close()


if __name__ == '__main__':
    # drop_db('multiplication')
    drop_db('users')
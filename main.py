import datetime
import random
import sqlite3

import pandas as pd


def full_scan():
    # make all examples
    all_examples = []
    for a in range(2, 10):
        for b in range(2, 10):
            all_examples.append([a, b])
    random.shuffle(all_examples)
    # print(all_examples)
    zzz = input('Ready?? Put the cursor to console and press ENTER')
    for example in all_examples:
        while True:
            try:
                start_time = datetime.datetime.now()
                example.append(int(input(f"{example[0]} * {example[1]} = ")))
                example.append((datetime.datetime.now() - start_time).total_seconds())
                if example[0] * example[1] == example[2]:
                    example.append(1)
                else:
                    example.append(0)
                break
            except:
                print("Not correct input")
        # print(example)
        to_sql(user_id, session_id, example[0], example[1], example[2], example[3], example[4])
    print("Well Done!!! :))")


def repeat():
    df = pd.read_sql_query(sql='SELECT * FROM multiplication', con=con)
    df1 = df[df.user_id == user_id] \
        .groupby(["a", "b"], as_index=False) \
        .agg({'duration': 'mean', 'result': 'mean'}) \
        .sort_values(by='duration', ascending=False)
    df1 = df1[(df1.duration >= df1.duration.quantile(q=0.65)) | (df1.result <= 0.75)]
    a_list = df1.a.to_list()
    b_list = df1.b.to_list()
    all_examples = list(map(lambda a, b: [a, b], a_list, b_list))
    for example in all_examples:
        print(f"{example[0]} * {example[1]} = {example[0] * example[1]}", end=" ")
        input("Press ENTER")
    zzz = input('Ready to the test?? Put the cursor to console and press ENTER')
    for example in all_examples:
        while True:
            try:
                start_time = datetime.datetime.now()
                example.append(int(input(f"{example[0]} * {example[1]} = ")))
                example.append((datetime.datetime.now() - start_time).total_seconds())
                if example[0] * example[1] == example[2]:
                    example.append(1)
                else:
                    example.append(0)
                break
            except:
                print("Not correct input")
        # print(example)
        to_sql(user_id, session_id, example[0], example[1], example[2], example[3], example[4])
    print("Well Done!!! :))")


def create_db():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS multiplication (
            user_id  INTEGER,
            session_id INTEGER,
            a  INTEGER,
            b  INTEGER,
            c  INTEGER,
            duration  REAL,
            result INTEGER);
            """)
    con.commit()


def to_sql(us_id, ses_id, a, b, c, duration, result):
    cur.execute('INSERT INTO multiplication VALUES (?,?,?,?,?,?,?)', [us_id, ses_id, a, b, c, duration, result])
    con.commit()


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    con = sqlite3.connect('multi_db.db')
    cur = con.cursor()
    create_db()
    user_id = 3
    username = 'Vita'
    print_hi(username)
    last_session = cur.execute(f'SELECT max(session_id) FROM multiplication WHERE user_id = {user_id}').fetchone()[0]
    if not isinstance(last_session, int):
        last_session = 0
    session_id = last_session + 1
    full_scan()


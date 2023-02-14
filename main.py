import datetime
import random
import sqlite3
import sys

import pandas as pd


def menu(user):
    print('='*35)
    menu_options = {
        1: 'Users',
        2: 'Multiplication table scan',
        3: 'Mistakes and long answers',
        4: 'Statistics',
        5: 'Exit'
    }

    def print_menu():
        for key in menu_options.keys():
            print(key, '--', menu_options[key])

    def option1():
        print('Not ready yet ;))')
        menu(user)

    def option2():
        full_scan(user)

    def option3():
        repeat(user)

    def option4():
        print('Not yet ;))')
        menu(user)

    while True:
        print_menu()
        option = ''
        try:
            option = int(input('Enter your choice: '))
        except ValueError:
            print('Wrong input. Please enter a number ...')
        # Check what choice was entered and act accordingly
        if option == 1:
            option1()
        elif option == 2:
            option2()
        elif option == 3:
            option3()
        elif option == 4:
            option4()
        elif option == 5:
            print('Thanks you, come back again!')
            exit()
        else:
            print('Invalid option. Please enter a number between 1 and 5.')


def full_scan(user):
    # make all examples
    all_examples = []
    for a in range(2, 10):
        for b in range(2, 10):
            all_examples.append([a, b])
    result = []
    [result.append(x) for x in all_examples if x not in result]
    solve_examples(user, result)


def solve_examples(user, lst_examples):
    last_session = cur.execute(f'SELECT max(session_id) FROM multiplication WHERE user_id = {user}').fetchone()[0]
    if not isinstance(last_session, int):
        last_session = 0
    session_id = last_session + 1
    all_examples = lst_examples
    random.shuffle(all_examples)
    # print(all_examples)
    zzz = input('Ready to the test?? press ENTER ... ')
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
        to_sql(user, session_id, example[0], example[1], example[2], example[3], example[4])
    print_results(user, session_id)


def repeat(user):
    df = pd.read_sql_query(sql='SELECT * FROM multiplication', con=con)
    df1 = df[df.user_id == user] \
        .groupby(["a", "b"], as_index=False) \
        .agg({'duration': 'mean', 'result': 'mean'}) \
        .sort_values(by='duration', ascending=False)
    df1 = df1[(df1.duration >= df1.duration.quantile(q=0.75)) | (df1.result <= 0.75)]
    a_list = df1.a.to_list()
    b_list = df1.b.to_list()
    all_examples = list(map(lambda a, b: [a, b], a_list, b_list))
    random.shuffle(all_examples)
    for example in all_examples:
        print(f"{example[0]} * {example[1]} = {example[0] * example[1]}", end=" ")
        zzz = input("  ...remember and press ENTER  ")
    solve_examples(user, all_examples)


def print_results(user, session):
    results = cur.execute('''
                            SELECT 
                              time(SUM(duration), 'unixepoch') spent_time,
                              COUNT(result) - sum(result) errors,
                              COUNT(result) total,
                              round(100.0*sum(result)/COUNT(result), 1) success_score,
                              round(SUM(duration)/COUNT(result),1) avg_time,
                            FROM multiplication m 
                            WHERE user_id = (?) AND session_id = (?) 
                          ''', [user, session]).fetchone()
    print("Well Done!!! :))")
    print(f'Time in game {results[0]},\nErrors: {results[1]}/{results[2]}, \nSuccess score: {results[3]}%')
    print(f'Average Answer Time: {results[4]} sec')
    menu(user)


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
    print(f'Hi, {name}')


if __name__ == '__main__':
    con = sqlite3.connect('multi_db.db')
    cur = con.cursor()
    create_db()
    user_id = 1
    username = 'Vita'
    print_hi(username)
    print('Put the cursor to console and press ENTER')
    menu(user_id)


import datetime
import random
import sqlite3
import os

import pandas as pd
from tabulate import tabulate

from database.sql_query import create_tables_db, load_to_sql, print_results, load_to_sessions

con = sqlite3.connect('database/multi_db_2.db')
cur = con.cursor()


def print_hi(user_name):
    print('=' * 35)
    print(f'Hi, {user_name}')


def full_scan(user_id):
    # make all examples
    all_examples = []
    for a in range(2, 10):
        for b in range(2, 10):
            all_examples.append([a, b])
    examples = []
    [examples.append(x) for x in all_examples if x not in examples]
    solve_examples(user_id, examples)


def solve_examples(user_id, list_examples):
    last_session = cur.execute(f'SELECT max(session_id) FROM sessions').fetchone()[0]
    last_user_session = cur.execute(f'SELECT max(session_user_id) FROM sessions WHERE user_id = {user_id}').fetchone()[0]
    if not isinstance(last_session, int):
        last_session = 0
    if not isinstance(last_user_session, int):
        last_user_session = 0
    # print('last_session is .. ', last_session)
    session_id = last_session + 1
    # print('last_user_session is .. ', last_user_session)
    user_session_id = last_user_session + 1
    random.shuffle(list_examples)
    zzz = input('Ready to the test?? press ENTER ... ')
    n, n_all = 1, len(list_examples)
    for example in list_examples:
        while True:
            try:
                start_time = datetime.datetime.now()
                example.append(int(input(f"{n} of {n_all}    {example[0]} * {example[1]} = ")))  # ex[0]=a,ex[1]=b,ex[3]=c
                example.append(round((datetime.datetime.now() - start_time).total_seconds(), 2))  # ex[4] = duration
                if example[0] * example[1] == example[2]:
                    example.append(1)
                else:
                    example.append(0)
                n += 1
                break
            except ValueError:
                print("Not correct input")
        load_to_sql(session_id, example[0], example[1], example[2], example[3], example[4])
    totals = cur.execute('''
                    SELECT 
                      time(SUM(duration), 'unixepoch') spent_time,
                      COUNT(result) total
                    FROM multiplication m 
                    WHERE session_id = (?) 
                  ''', [session_id]).fetchone()
    load_to_sessions(user_id, user_session_id, datetime.datetime.today().date(), totals[0], totals[1])
    print("Well Done!!! :))")
    print_results(user_id, session_id)


def repeat(user_id):
    sql_q = """
                SELECT
                    a.session_id ,
                    a.a ,
                    a.b ,
                    a.duration ,
                    a."result" ,
                    b.user_id
                FROM multiplication a
                LEFT JOIN sessions b
                    ON a.session_id = b.session_id
            """
    df = pd.read_sql_query(sql=sql_q, con=con)
    df1 = df[df.user_id == user_id] \
        .groupby(["a", "b"], as_index=False) \
        .agg({'duration': 'mean', 'result': 'mean'}) \
        .sort_values(by='duration', ascending=False)
    df1 = df1[(df1.duration >= df1.duration.quantile(q=0.75)) | (df1.result <= 0.75)].head(36)
    a_list = df1.a.to_list()
    b_list = df1.b.to_list()
    all_examples = list(map(lambda a, b: [a, b], a_list, b_list))
    random.shuffle(all_examples)
    for example in all_examples:
        print(f"{example[0]} * {example[1]} = {example[0] * example[1]}", end=" ")
        zzz = input("  ...remember and press ENTER  ")
    solve_examples(user_id, all_examples)


def menu():
    create_tables_db()
    user_id = 0
    user_name = 'No_Name'
    print_hi(user_name)
    print('Put the cursor to console and choose user, press "1" ENTER')

    option = ''
    while True:
        if user_id == 0 and option == '':
            option = 1
        elif user_id != 0 and option != '':
            print('=' * 35)
            menu_options = {
                1: 'Choose User',
                2: 'Crete New User',
                3: 'Scan Multiplication table',
                4: 'Mistakes and long answers',
                5: 'Statistics for your sessions',
                6: 'Winners',
                0: 'Exit'
            }
            for key in menu_options.keys():
                print(key, '--', menu_options[key])
            try:
                option = int(input('Enter your choice: '))
            except ValueError:
                print('Wrong input. Please enter a number ...')
        # Check what choice was entered
        if option == 1:
            # 1: 'Choose User'
            df_names = pd.read_sql_query(sql='SELECT user_id, name FROM users', con=con)
            print('Choose your name or "0" to create new user:')
            print(tabulate(df_names, headers="keys", tablefmt='psql', showindex=False))
            try:
                user_id = int(input('Input your id number... '))
                if user_id == 0:
                    print('NULL')
                    option = 2
                else:
                    user_name = cur.execute("SELECT name FROM users WHERE user_id =(?)", [user_id]).fetchone()[0]
                    print_hi(user_name)
                # Добавить проверку на есть ли user_id в БД

            except ValueError:
                print('Wrong input. Please enter a number ...')
            # exit()

        elif option == 2:
            # 2: 'Crete New User'
            print('New User!')
            user_name = input('Input your Name... ')
            # Если ноль то выйти
            cur.execute("INSERT INTO users (name) VALUES (?)", [user_name])
            con.commit()
            print('Done!')
            print_hi(user_name)
            user_id = cur.execute("SELECT user_id FROM users WHERE name =(?)", [user_name]).fetchone()[0]

        elif option == 3:
            # 3: 'Scan Multiplication table'
            full_scan(user_id)
        elif option == 4:
            # 4: 'Mistakes and long answers'
            repeat(user_id)
        elif option == 5:
            # 5: 'Statistics'
            query = f"""
                SELECT 
                    b.session_user_id  , 
                    COUNT(a."result") - SUM(a."result") wrong_answers,
                    SUM("result") correct_answers,
                    ROUND(AVG(duration),1) avg_answer_time
                FROM multiplication a 
                LEFT JOIN sessions b 
                ON a.session_id = b.session_id 
                WHERE b.user_id = {user_id}
                GROUP BY b.session_id
                """
            print('This is your results')
            print(tabulate(pd.read_sql_query(sql=query, con=con), headers="keys", tablefmt='psql', showindex=False))
            # need to add try/except block
            session = int(input('Input the number of session to see more details and heatmap: '))

            # last_session = cur.execute("""
            #                 SELECT max(session_id) max_session_id
            #                 FROM multiplication m
            #                 WHERE user_id = (?)
            #             """, [user_id]).fetchone()[0]

            print_results(user_id, session)
            print_hi(user_name)

        elif option == 6:
            # 6:'Winners'
            query = """
                        SELECT
                            a.name Name,
                            COUNT(c.result) "Solved examples",
                            COUNT(c.result) - SUM(c.result) "Wrong answers",
                            SUM(c.result) "Correct answers",
                            round(100.0*sum(c.result)/COUNT(c.result), 1) "Success score",
                            ROUND(AVG(c.duration),1) "Average answer time"
                        FROM 
                            users a
                            JOIN sessions b on a.user_id = b.user_id
                            JOIN multiplication c on b.session_id = b.session_id
                        GROUP BY a.name
                        ORDER BY "Solved examples" DESC
                        """
            print(tabulate(pd.read_sql_query(sql=query, con=con), headers="keys", tablefmt='psql', showindex=False))
            print_hi(user_name)

        elif option == 0:
            # 0: 'Exit'
            print(f'Thanks you {user_name}, come back again!')
            exit()
        else:
            print('Invalid option. Please enter a number between 1 and 6. or 0 to exit')


if __name__ == '__main__':
    menu()

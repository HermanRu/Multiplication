import datetime
import random
import sqlite3
import os

import pandas as pd
import plotly.express as px
from tabulate import tabulate


def print_hi(name):
    print(f'Hi, {name}')


def full_scan(u_id):
    # make all examples
    all_examples = []
    for a in range(2, 10):
        for b in range(2, 10):
            all_examples.append([a, b])
    examples = []
    [examples.append(x) for x in all_examples if x not in examples]
    solve_examples(u_id, examples)


def solve_examples(u_id, list_examples):
    last_session = cur.execute(f'SELECT max(session_id) FROM multiplication WHERE user_id = {u_id}').fetchone()[0]
    if not isinstance(last_session, int):
        last_session = 0
    session_id = last_session + 1
    random.shuffle(list_examples)
    zzz = input('Ready to the test?? press ENTER ... ')
    n, n_all = 1, len(list_examples)
    for example in list_examples:
        while True:
            try:
                start_time = datetime.datetime.now()
                example.append(int(input(f"{n} of {n_all}    {example[0]} * {example[1]} = ")))
                example.append((datetime.datetime.now() - start_time).total_seconds())
                if example[0] * example[1] == example[2]:
                    example.append(1)
                else:
                    example.append(0)
                n += 1
                break
            except ValueError:
                print("Not correct input")
        to_sql(u_id, session_id, example[0], example[1], example[2], example[3], example[4])
    print("Well Done!!! :))")
    print_results(u_id, session_id)


def repeat(u_id):
    df = pd.read_sql_query(sql='SELECT * FROM multiplication', con=con)
    df1 = df[df.user_id == u_id] \
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
    solve_examples(u_id, all_examples)


def print_results(u_id, session_id):
    results = cur.execute('''
                            SELECT 
                              time(SUM(duration), 'unixepoch') spent_time,
                              COUNT(result) - sum(result) errors,
                              COUNT(result) total,
                              round(100.0*sum(result)/COUNT(result), 1) success_score,
                              round(SUM(duration)/COUNT(result),1) avg_time
                            FROM multiplication m 
                            WHERE user_id = (?) AND session_id = (?) 
                          ''', [u_id, session_id]).fetchone()
    print(f'Time in game {results[0]}')
    print(f'Errors: {results[1]}/{results[2]}')
    print(f'Success score: {results[3]}%')
    print(f'Average Answer Time: {results[4]} sec')
    density_heatmap(f'SELECT * FROM multiplication WHERE user_id = {u_id} AND session_id = {session_id}')


def density_heatmap(sql_query):
    df = pd.read_sql_query(sql=sql_query, con=con)

    fig1 = px.density_heatmap(df, x='a', y='b', z="duration", histfunc="avg",
                              nbinsx=9, nbinsy=9, text_auto='.1f', height=500, width=600)
    fig2 = px.density_heatmap(df, x='a', y='b', z="result", histfunc="avg",
                              nbinsx=9, nbinsy=9, text_auto='.1f', height=500, width=600)
    fig1.update_xaxes(dtick=1)
    fig1.update_yaxes(dtick=1)
    fig2.update_xaxes(dtick=1)
    fig2.update_yaxes(dtick=1)

    fig1.write_image("duration_heatmap_tmp.png")
    fig2.write_image("result_heatmap_tmp.png")

    # os.startfile("duration_heatmap_tmp.png")


def create_db():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS multiplication (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER,
            session_id INTEGER,
            a  INTEGER,
            b  INTEGER,
            c  INTEGER,
            duration  REAL,
            result INTEGER,
            FOREIGN KEY (user_id)  REFERENCES users (user_id)
            );""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT,
            other TEXT);
            """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id  INTEGER,
    session_id INTEGER,
    date TEXT,
    session_duration REAL,
    solved_examples INTEGER);
    """)
    con.commit()


def to_sql(us_id, ses_id, a, b, c, duration, result):
    cur.execute('INSERT INTO multiplication (user_id, session_id, a, b, c, duration, "result") VALUES (?,?,?,?,?,?,?)',
                [us_id, ses_id, a, b, c, duration, result])
    con.commit()


if __name__ == '__main__':
    con = sqlite3.connect('multi_db.db')
    cur = con.cursor()
    create_db()
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
                    session_id,
                    COUNT(result) - SUM(result) wrong_answers,
                    SUM(result) correct_answers,
                    ROUND(AVG(duration),1) avg_answer_time
                FROM multiplication
                WHERE user_id = {user_id}
                GROUP BY session_id
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
                            SUM(b.result) \"Solved examples\",
                            COUNT(result) - SUM(result) \"Wrong answers\",
                            SUM(result) \"Correct answers\",
                            round(100.0*sum(result)/COUNT(result), 1) \"Success score\",
                            ROUND(AVG(duration),1) \"Average answer time\"
                        FROM 
                            users a
                            JOIN multiplication b on a.user_id = b.user_id
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
